# import colander
from datetime import datetime
import dateutil
import deform
from deform import ValidationFailure
from pkg_resources import resource_filename
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import (
    get_localizer,
    TranslationStringFactory
)
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from sqlalchemy.exc import (
    InvalidRequestError,
    IntegrityError
)

from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
from c3spartyticketing.models import (
    DBSession,
    PartyTicket,
)
from c3spartyticketing.ticket_schema_nonmember import ticket_nonmember_schema
from c3spartyticketing.utils import make_random_string

_ = TranslationStringFactory('c3spartyticketing')


def translator(term):
    return get_localizer(get_current_request()).translate(term)

my_template_dir = resource_filename('c3spartyticketing', 'templates/')
deform_template_dir = resource_filename('deform', 'templates/')
zpt_renderer = deform.ZPTRendererFactory(
    [
        my_template_dir,
        deform_template_dir,
    ],
    translator=translator,
)


@view_config(route_name='nonmember',
             renderer='templates/nonmember.pt')
def nonmember_view(request):
    """
    The view nonmember-users use to order a ticket.

    Renderer:
        templates/nonmember.pt
    """

    # ## clear session
    request.session['userdata'] = {}
    request.session['derivedvalues'] = {}
    request.session['flags'] = {}
    # XXX think about a nicer abstract way to save derived values (->form
    # object) and flags, which control the flow

    # distinction member / nonmember
    request.session['flags']['isMember'] = True

    # ## pick route
    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    if today > registration_end:
        print('date check: registration is finished. redirecting ...')
        return HTTPFound(location=request.route_url('nonmember_end'))
    # route = check_route(request, 'party')
    # if isinstance(route, HTTPRedirection):
    #    return route

    # ## generate appstruct
    # appstruct = ticket_appstruct(request, 'party')
    appstruct = {}

    # ## generate form
    schema = ticket_nonmember_schema(request, appstruct)
    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit'))
        ],
        # use_ajax=True,
        renderer=zpt_renderer
    )
    form.set_appstruct(appstruct)

    # if the form has NOT been used and submitted, remove error messages if any
    if 'submit' not in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        print "submitted!"
        controls = request.POST.items()
        print controls

        # ## validation of user input

        try:
            print 'about to validate form input'
            appstruct = form.validate(controls)
            print 'done validating form input'
            print("the appstruct from the form: %s \n" % appstruct)
            # for thing in appstruct:
            #     print(u"the thing: %s") % thing
            #     print(u"type: %s") % type(thing)

        except ValidationFailure, e:
            print(e)
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{
                'form': e.render(),
                'formerror': True
            }

        # ## derived values

        # map option to price
        the_values = {
            'ticket_bc_attendance': int(request.bc_cost),
            'ticket_bc_buffet': int(request.bc_food_cost),
            'ticket_tshirt': 0,
            'ticket_all': 42,  # unused
        }

        # map supporter tickets to price
        the_support = {
            1: int(request.supporter_M),
            2: int(request.supporter_L),
            3: int(request.supporter_XL),
            4: int(request.supporter_XXL),
        }

        # bc: buffet only when attended
        if 'attendance' not in appstruct['ticket']['ticket_bc']:
            appstruct['ticket']['ticket_bc'].discard('buffet')

        # calculate the total sum and discount
        print("calculate the total sum and discount")
        _the_total = 0
        _support = 0
        if 'attendance' in appstruct['ticket']['ticket_bc']:
            _the_total += the_values.get('ticket_bc_attendance')
        if 'buffet' in appstruct['ticket']['ticket_bc']:
            _the_total += the_values.get('ticket_bc_buffet')
        # if appstruct['ticket']['ticket_tshirt']:
        #    _the_total += the_values.get('ticket_tshirt')
        for support in appstruct['ticket']['ticket_support']:
            _the_total += the_support.get(int(support))
            _support += the_support.get(int(support))

        appstruct['ticket']['the_total'] = _the_total
        print("_the_total: %s" % _the_total)

        request.session['derivedvalues'] = {
            'the_total': _the_total,
            'support': _support
        }
        request.session['appstruct'] = appstruct

        # empty the messages queue (as validation worked anyways)
        deleted_msg = request.session.pop_flash()
        del deleted_msg

        # set flag to ensure, user is coming from confirmed view (validation)
        request.session['flags'] = {
            'confirm': True
        }

        return HTTPFound(  # redirect to confirm page
            location=request.route_url('nonmember_confirm'),
        )

    # if the form was submitted and gathered info shown on the success page,
    # BUT the user wants to correct their information:
    else:
        # remove annoying message from other session
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        if ('appstruct' in request.session):
            appstruct = request.session['appstruct']
            form.set_appstruct(appstruct)

    html = form.render()
    return {
        'form': html,
        'reedit': ('reedit' in request.GET)
    }


@view_config(route_name='nonmember_confirm',
             renderer='templates/nonmember_confirm.pt')
def nonmember_confirm_view(request):
    """
    The nonmember form was submitted correctly.
    Show the result for the user to confirm.

    Renderer:
        templates/nonmember_confirm.pt
    """

    # ## pick route
    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    if today > registration_end:
        print('date check: registration is finished. redirecting ...')
        return HTTPFound(location=request.route_url('nonmember_end'))
    # route = check_route(request, 'confirm')
    # if isinstance(route, HTTPRedirection):
    #    return route

    # ## generate appstruct
    # appstruct = ticket_appstruct(request, 'confirm')

    if 'appstruct' not in request.session:
        return HTTPFound(location=request.route_url('nonmember'))

    # reedit: user wants to re-edit her data
    if 'reedit' in request.POST:
        return HTTPFound(location=request.route_url('nonmember')+'?reedit')

    # order: user confirmed the data
    if 'confirmed' in request.POST:
        request.session['flags'] = {
            'confirmed': True
        }
        return HTTPFound(location=request.route_url('nonmember_success'))

    appstruct = request.session['appstruct']

    # ## generate form
    schema = ticket_nonmember_schema(
        request, appstruct, readonly=True
    )
    button_submit_text = _(u'Submit & Buy')
    if appstruct['ticket']['the_total'] == 0:
        button_submit_text = _(u'Submit')
    form = deform.Form(
        schema,
        buttons=[
            deform.Button('confirmed', button_submit_text),
            deform.Button('reedit', _(u'Wait, I might have to change...'))
        ],
        renderer=zpt_renderer
    )

    return {
        'readonlyform': form.render(
            appstruct=request.session['appstruct'])}


@view_config(route_name='nonmember_success',
             renderer='templates/nonmember_success.pt')
def nonmember_success_view(request):
    """
    The user has confirmed the order

    1. save to db
    2. send emails (usermail, accmail)
    3. show userfeedback

    Renderer:
        templates/nonmember_success.pt
    """

    # ## pick route
    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    if today > registration_end:
        print('date check: registration is finished. redirecting ...')
        return HTTPFound(location=request.route_url('nonmember_end'))
    # route = check_route(request, 'confirm')
    # if isinstance(route, HTTPRedirection):
    #    return route

    # confirmed: test flag
    if 'flags' not in request.session \
       or 'confirmed' not in request.session['flags']:
        return HTTPFound(location=request.route_url('nonmember'))

    if 'appstruct' not in request.session:
        return HTTPFound(location=request.route_url('nonmember'))

    # ## generate appstruct
    appstruct = request.session['appstruct']

    # ### save to db

    # make confirmation code
    randomstring = make_random_string()

    # create in db
    ticket = PartyTicket(
        token='',
        firstname=appstruct['personal']['firstname'],
        lastname=appstruct['personal']['lastname'],
        email=appstruct['personal']['email'],
        password='',  # appstruct['person']['password'],
        locale=appstruct['ticket']['_LOCALE_'],
        email_is_confirmed=False,
        email_confirm_code=randomstring,
        date_of_submission=datetime.now(),
        num_tickets=1,
        ticket_gv_attendance=3,
        ticket_bc_attendance=(
            'attendance' in appstruct['ticket']['ticket_bc']),
        ticket_bc_buffet=(
            'buffet' in appstruct['ticket']['ticket_bc']),
        # ticket_tshirt=appstruct['ticket']['ticket_tshirt'],
        # ticket_tshirt_type=appstruct['tshirt']['tshirt_type'],
        # ticket_tshirt_size=appstruct['tshirt']['tshirt_size'],
        ticket_tshirt=False,
        ticket_tshirt_type=0,
        ticket_tshirt_size=0,
        ticket_all=False,
        ticket_support=(
            '1' in appstruct['ticket']['ticket_support']),
        ticket_support_l=(
            '2' in appstruct['ticket']['ticket_support']),
        ticket_support_xl=(
            '3' in appstruct['ticket']['ticket_support']),
        ticket_support_xxl=(
            '4' in appstruct['ticket']['ticket_support']),
        support=request.session['derivedvalues']['support'],
        discount=0,
        the_total=request.session['derivedvalues']['the_total'],
        rep_firstname='',
        rep_lastname='',
        rep_street='',
        rep_zip='',
        rep_city='',
        rep_country='',
        rep_type=None,
        guestlist=False,
        user_comment=appstruct['ticket']['comment'],
        )
    ticket.membership_type = 'nonmember'
    try:
        DBSession.add(ticket)
        print('save to db: created.')
        appstruct['email_confirm_code'] = randomstring  # XXX
        #                                    check duplicates
    except InvalidRequestError, e:  # pragma: no cover
        print("InvalidRequestError! %s") % e
    except IntegrityError, ie:  # pragma: no cover
        print("IntegrityError! %s") % ie

    # ## render emails

    # sanity check of local_name; XXX put into subscripber.py
    lang = request.registry.settings['pyramid.default_locale_name']
    langs = request.registry.settings['available_languages'].split()
    if request.locale_name in langs:
        lang = request.locale_name

    #######################################################################
    """
    Here we send email to the person who wants a ticket.

    If the total is 0 because the barcamp is free, then send mail,
    but no transfer information. choose a different template
    """
    usermail_nonmember_subject = u'C3S Barcamp: your order'
    if lang == "de":
        usermail_nonmember_subject = 'C3S Barcamp: Deine Bestellung'
    if request.session['derivedvalues']['the_total'] == 0:
        usermail_nonmember = render(
            'templates/mails/usermail_nonmember-free-' + lang + '.pt',
            {
                'firstname': appstruct['personal']['firstname'],
                'lastname': appstruct['personal']['lastname'],
            }
        )
    else:
        usermail_nonmember = render(
            'templates/mails/usermail_nonmember-'+lang+'.pt',
            {
                'firstname': appstruct['personal']['firstname'],
                'lastname': appstruct['personal']['lastname'],
                'the_total': request.session['derivedvalues']['the_total'],
                'email_confirm_code': appstruct['email_confirm_code'],
                'fully_paid_date': request.fully_paid_date,
            }
        )

    #######################################################################
    accmail_subject = u'[C3S_PT] neues nonmember ticket'
    accmail_body = render(
        'templates/mails/accmail_nonmember.pt',
        {
            'firstname': appstruct['personal']['firstname'],
            'lastname': appstruct['personal']['lastname'],
            'email': appstruct['personal']['email'],
            'bc_attendance': (
                'attendance' in appstruct['ticket']['ticket_bc'] or 'False'),
            'bc_buffet': (
                'buffet' in appstruct['ticket']['ticket_bc'] or 'False'),
            'the_total': appstruct['ticket']['the_total'],
            'comment': appstruct['ticket']['comment'],
            # 'tshirt': appstruct['ticket']['ticket_tshirt'] or 'False',
            # 'tshirt_type': appstruct['tshirt']['tshirt_type'],
            # 'tshirt_size': appstruct['tshirt']['tshirt_size'],
            'supporter': (
                '1' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_l': (
                '2' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_xl': (
                '3' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_xxl': (
                '4' in appstruct['ticket']['ticket_support'] or 'False')
        }
    )

    # ## send mails
    mailer = get_mailer(request)

    # ## send usermail
    usermail_obj = Message(
        subject=usermail_nonmember_subject,
        sender=request.registry.settings['c3spartyticketing.mail_sender'],
        recipients=[appstruct['personal']['email']],
        body=usermail_nonmember
    )

    if 'true' in request.registry.settings['testing.mail_to_console']:
        print('----- 8< ------------------------------------ user mail ---')
        print(usermail_nonmember.encode('utf-8'))
        print('----- >8 --------------------------------------------------')
    else:
        mailer.send(usermail_obj)

    # ## send accmail
    if 'true' in request.registry.settings['testing.mail_to_console']:
        print('----- 8< ------------------------------ accountant mail ---')
        print(accmail_body.encode('utf-8'))
        print('----- 8< ---------------------------------------------------')
    else:
        accmail_obj = Message(
            subject=accmail_subject,
            sender=request.registry.settings['c3spartyticketing.mail_sender'],
            recipients=[
                request.registry.settings['c3spartyticketing.mail_rec']],
            body=encrypt_with_gnupg(accmail_body)
        )
        mailer.send(accmail_obj)

    # make the session go away
    request.session.invalidate()
    return {
        'firstname': appstruct['personal']['firstname'],
        'lastname': appstruct['personal']['lastname']
    }


@view_config(route_name='nonmember_end',
             renderer='templates/nonmember_end.pt')
def nonmember_end_view(request):
    """
    Show message after registration time is over.

    Renderer:
        templates/nonmember_end.pt
    """
    # ## pick route
    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    if today <= registration_end:
        return HTTPFound(location=request.route_url('nonmember'))

    return {}
