# -*- coding: utf-8 -*-
"""
This module holds the main Ticket forms for members.

There are different forms, depending on where the user comes from:

**C3S Members**
  have received an invitation email with a link (containing a **token**).
  This link triggers c3sPartyTicketing to ask relevant information
  via REST-API call from c3sMembership, so first and last name
  as well as membership type are known to c3sPartyTicketing.

"""
from datetime import datetime
import dateutil.parser
import deform
from deform import ValidationFailure
from pkg_resources import resource_filename

from pyramid.httpexceptions import (
    HTTPRedirection,
    HTTPFound
)
from pyramid.i18n import (
    TranslationStringFactory,
    get_localizer,
)
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config

# from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import (
    InvalidRequestError,
    IntegrityError
)

from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
from c3spartyticketing.models import (
    DBSession,
    PartyTicket,
)
from c3spartyticketing.ticket_schema_member import ticket_member_schema
from c3spartyticketing.ticket_schema_member_gvonly import (
    ticket_member_gvonly_schema)
from c3spartyticketing.utils import make_random_string
from c3spartyticketing.views import (
    check_route,
    ticket_appstruct,
)

_ = TranslationStringFactory('c3spartyticketing')

# deform_templates = resource_filename('deform', 'templates')

# c3spartyticketing_templates = resource_filename(
#    'c3spartyticketing', 'templates')

# my_search_path = (deform_templates, c3spartyticketing_templates)


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


@view_config(route_name='party',
             renderer='templates/party.pt')
def party_view(request):
    """
    The view users use to order a ticket.

    Renderer:
        templates/party.pt
    """

    # ## pick route
    route = check_route(request, 'party')
    if isinstance(route, HTTPRedirection):
        return route

    # ## generate appstruct
    appstruct = ticket_appstruct(request, 'party')

    # ## generate form
    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    gvonly = False
    if today > registration_end:
        gvonly = True
        schema = ticket_member_gvonly_schema(
            request, appstruct, readonly=False)
    else:
        schema = ticket_member_schema(request, appstruct, readonly=False)

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
            print("the appstruct from the form: %s \n") % appstruct
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
                'firstname': appstruct['ticket']['firstname'],
                'lastname': appstruct['ticket']['lastname'],
                'email': appstruct['ticket']['email'],
                'formerror': True,
                'gvonly': gvonly
            }

        # ## derived values

        # map option to price
        the_values = {
            'ticket_gv_attendance': 0,
            'ticket_bc_attendance':  int(request.bc_cost),
            'ticket_bc_buffet':  int(request.bc_food_cost),
            'ticket_tshirt': 0,
            'ticket_all': 42,  # unused
        }

        # no shirts this time!
        appstruct['ticket']['ticket_tshirt'] = False

        # map option to discount
        # the_discounts = {
        #    'ticket_all': -2.5
        # }

        # map supporter tickets to price
        the_support = {
            1: int(request.supporter_M),
            2: int(request.supporter_L),
            3: int(request.supporter_XL),
            4: int(request.supporter_XXL),
        }

        if gvonly:
            request.session['derivedvalues'] = {
                'the_total': 0,
                'discount': 0,
                'support': 0
            }
            appstruct['ticket']['the_total'] = 0
            appstruct['ticket']['discount'] = 0
        else:
            # option 'all' equivalent to all options checked
            if (
                    (appstruct['ticket']['ticket_gv'] == 1) and
                    (set(
                        ['attendance', 'buffet']).issubset(
                            appstruct['ticket']['ticket_bc'])) and
                    (appstruct['ticket']['ticket_tshirt'])
            ):
                appstruct['ticket']['ticket_all'] = True

            # aint no shirt, no all
            appstruct['ticket']['ticket_all'] = False
            appstruct['ticket']['ticket_tshirt'] = False
            # ensure options equivalent to option 'all'
            if appstruct['ticket']['ticket_all']:
                appstruct['ticket']['ticket_gv'] = 1
                appstruct['ticket']['ticket_tshirt'] = True
                appstruct['ticket']['ticket_bc'].add('attendance')
                appstruct['ticket']['ticket_bc'].add('buffet')

            # bc: buffet only when attended
            if 'attendance' not in appstruct['ticket']['ticket_bc']:
                appstruct['ticket']['ticket_bc'].discard('buffet')

            # calculate the total sum and discount
            print("calculate the total sum and discount")
            _the_total = 0
            _discount = 0
            _support = 0
            if appstruct['ticket']['ticket_all']:
                print("all active")
                # _discount = the_discounts.get('ticket_all')
                _the_total = the_values.get('ticket_all')
            else:
                if 'attendance' in appstruct['ticket']['ticket_bc']:
                    _the_total += the_values.get('ticket_bc_attendance')
                if 'buffet' in appstruct['ticket']['ticket_bc']:
                    _the_total += the_values.get('ticket_bc_buffet')
                if appstruct['ticket']['ticket_tshirt']:
                    _the_total += the_values.get('ticket_tshirt')
                for support in appstruct['ticket']['ticket_support']:
                    _the_total += the_support.get(int(support))
                    _support += the_support.get(int(support))

            appstruct['ticket']['the_total'] = _the_total
            print("_the_total: %s" % _the_total)
            appstruct['ticket']['discount'] = _discount
            print("_discount: %s" % _discount)

            request.session['derivedvalues'] = {
                'the_total': _the_total,
                'discount': _discount,
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
            location=request.route_url('confirm'),
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
        'firstname': appstruct['ticket']['firstname'],
        'lastname': appstruct['ticket']['lastname'],
        'email': appstruct['ticket']['email'],
        'reedit': ('reedit' in request.GET),
        'gvonly': gvonly
    }


@view_config(route_name='confirm',
             renderer='templates/confirm.pt')
def confirm_view(request):
    """
    The form was submitted correctly. Show the result for the user to confirm.

    Renderer:
        templates/confirm.pt
    """

    # ## pick route
    route = check_route(request, 'confirm')
    if isinstance(route, HTTPRedirection):
        return route

    # ## generate appstruct
    appstruct = ticket_appstruct(request, 'confirm')

    # ## generate form
    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    gvonly = False
    if today > registration_end:
        gvonly = True  # unused?
        schema = ticket_member_gvonly_schema(
            request, request.session['appstruct'], readonly=True
        )
    else:
        schema = ticket_member_schema(
            request, request.session['appstruct'], readonly=True
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
        # use_ajax=True,
        renderer=zpt_renderer
    )

    return {
        'readonlyform': form.render(
            appstruct=request.session['appstruct'])}


@view_config(route_name='success',
             renderer='templates/success.pt')
def success_view(request):
    """
    The user has confirmed the order

    1. save to db (update, if token exists in db; create otherwise)
    2. send emails (usermail, accmail)
    3. show userfeedback

    Renderer:
        templates/success.pt
    """

    # ## pick route
    route = check_route(request, 'success')
    if isinstance(route, HTTPRedirection):
        return route

    # ## generate appstruct
    appstruct = ticket_appstruct(request, 'success')

    today = datetime.today().date()
    registration_end = dateutil.parser.parse(
        request.registry.settings['registration.end']
    ).date()
    gvonly = False
    if today > registration_end:
        gvonly = True

    if gvonly:
        appstruct['ticket']['ticket_bc'] = set()
        appstruct['ticket']['ticket_support'] = set()
        appstruct['ticket']['ticket_tshirt'] = False
        appstruct['ticket']['ticket_all'] = False
        appstruct['tshirt'] = {
            'tshirt_type': None,
            'tshirt_size': None
        }

    # ## save to db

    # make confirmation code
    randomstring = make_random_string()

    # update, if token exists in db; create otherwise
    if PartyTicket.has_token(request.session['userdata']['token']):
        ticket = PartyTicket.get_by_token(
            request.session['userdata']['token']
        )
        # just save those details that changed
        ticket.date_of_submission = datetime.now()
        ticket.ticket_gv_attendance = appstruct['ticket']['ticket_gv']
        ticket.ticket_bc_attendance = (
            'attendance' in appstruct['ticket']['ticket_bc']
        )
        ticket.ticket_bc_buffet = (
            'buffet' in appstruct['ticket']['ticket_bc']
        )
        # ticket.ticket_tshirt = appstruct['ticket']['ticket_tshirt']
        # ticket.ticket_tshirt_type = appstruct['tshirt']['tshirt_type']
        # ticket.ticket_tshirt_size = appstruct['tshirt']['tshirt_size']
        # ticket.ticket_all = appstruct['ticket']['ticket_all']
        ticket.ticket_tshirt = False
        ticket.ticket_tshirt_type = 0
        ticket.ticket_tshirt_size = 0
        ticket.ticket_all = False
        ticket.ticket_support = True if (
            '1' in appstruct['ticket']['ticket_support']) else False
        ticket.ticket_support_x = True if (
            '2' in appstruct['ticket']['ticket_support']) else False
        ticket.ticket_support_xl = True if (
            '3' in appstruct['ticket']['ticket_support']) else False
        ticket.ticket_support_xxl = True if (
            '4' in appstruct['ticket']['ticket_support']) else False
        ticket.support = request.session['derivedvalues']['support']
        ticket.discount = request.session['derivedvalues']['discount']
        ticket.the_total = request.session['derivedvalues']['the_total']
        ticket.rep_firstname = appstruct['representation']['firstname']
        ticket.rep_lastname = appstruct['representation']['lastname']
        ticket.rep_email = appstruct['representation']['email']
        ticket.rep_street = appstruct['representation']['street']
        ticket.rep_zip = appstruct['representation']['zip']
        ticket.rep_city = appstruct['representation']['city']
        ticket.rep_country = appstruct['representation']['country']
        ticket.rep_type = appstruct['representation']['representation_type']
        ticket.guestlist = False
        ticket.user_comment = appstruct['ticket']['comment']
        DBSession.flush()  # save to DB
        print('save to db: updated.')
        #  set the appstruct for further processing
        appstruct['email_confirm_code'] = ticket.email_confirm_code
        request.session['mtype'] = ticket.membership_type
    else:
        # to store the data in the DB, an object is created
        ticket = PartyTicket(
            token=request.session['userdata']['token'],
            firstname=request.session['userdata']['firstname'],
            lastname=request.session['userdata']['lastname'],
            email=request.session['userdata']['email'],
            password=u'',  # appstruct['person']['password'],
            locale=appstruct['ticket']['_LOCALE_'],
            email_is_confirmed=False,
            email_confirm_code=randomstring,
            date_of_submission=datetime.now(),
            num_tickets=1,
            ticket_gv_attendance=appstruct['ticket']['ticket_gv'],
            ticket_bc_attendance=(
                'attendance' in appstruct['ticket']['ticket_bc']),
            ticket_bc_buffet=(
                'buffet' in appstruct['ticket']['ticket_bc']),
            # ticket_tshirt=appstruct['ticket']['ticket_tshirt'],
            # ticket_tshirt_type=appstruct['tshirt']['tshirt_type'],
            # ticket_tshirt_size=appstruct['tshirt']['tshirt_size'],
            # ticket_all=appstruct['ticket']['ticket_all'],
            ticket_tshirt=False,  # appstruct['ticket']['ticket_tshirt'],
            ticket_tshirt_type=0,  # appstruct['tshirt']['tshirt_type'],
            ticket_tshirt_size=0,  # appstruct['tshirt']['tshirt_size'],
            ticket_all=False,  # appstruct['ticket']['ticket_all'],
            ticket_support=True if (
                '1' in appstruct['ticket']['ticket_support']) else False,
            ticket_support_l=True if (
                '2' in appstruct['ticket']['ticket_support']) else False,
            ticket_support_xl=True if (
                '3' in appstruct['ticket']['ticket_support']) else False,
            ticket_support_xxl=True if (
                '4' in appstruct['ticket']['ticket_support']) else False,
            support=request.session['derivedvalues']['support'],
            discount=request.session['derivedvalues']['discount'],
            the_total=request.session['derivedvalues']['the_total'],
            rep_firstname=appstruct['representation']['firstname'],
            rep_lastname=appstruct['representation']['lastname'],
            rep_street=appstruct['representation']['street'],
            rep_zip=appstruct['representation']['zip'],
            rep_city=appstruct['representation']['city'],
            rep_country=appstruct['representation']['country'],
            rep_type=appstruct['representation']['representation_type'],
            guestlist=False,
            user_comment=appstruct['ticket']['comment'],
            )
        ticket.rep_email = appstruct['representation']['email']
        ticket.membership_type = request.session['userdata']['mtype']

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
    usermail_gv_transaction_subject = \
        u'C3S General Assembly & Barcamp 2016: your participation & order'
    if lang == "de":
        usermail_gv_transaction_subject = (
            u'C3S Generalversammlung & Barcamp 2016: '
            u'Deine Teilnahme & Bestellung')
    usermail_gv_transaction = render(
        'templates/mails/usermail_gv_transaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'the_total': appstruct['ticket']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code'],
            'fully_paid_date': request.fully_paid_date,
        }
    )

    #######################################################################
    usermail_gv_notransaction_subject = \
        u'C3S General Assembly & Barcamp 2016: your participation'
    if lang == "de":
        usermail_gv_notransaction_subject = \
            u'C3S Generalversammlung & Barcamp 2016: Deine Teilnahme'
    usermail_gv_notransaction = render(
        'templates/mails/usermail_gv_notransaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'fully_paid_date': request.fully_paid_date,
        }
    )

    #######################################################################
    usermail_notgv_bc_subject = (
        u'C3S General Assembly & Barcamp 2016: your BarCamp ticket / '
        u'your cancellation of the general assembly')
    if lang == "de":
        usermail_notgv_bc_subject = (
            u'C3S Generalversammlung & Barcamp 2016: Dein Barcamp-Ticket / '
            u'Deine Absage der Generalversammlung')
    usermail_notgv_bc = render(
        'templates/mails/usermail_notgv_bc-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'the_total': appstruct['ticket']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code'],
            'fully_paid_date': request.fully_paid_date,
        }
    )

    #######################################################################
    usermail_notgv_notbc_transaction_subject = \
        u'C3S General Assembly & Barcamp 2016: your cancellation / your order'
    if lang == "de":
        usermail_notgv_notbc_transaction_subject = (
            u'C3S Generalversammlung & Barcamp 2016: '
            'Deine Absage / Deine Bestellung')
    usermail_notgv_notbc_transaction = render(
        'templates/mails/usermail_notgv_notbc_transaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'the_total': appstruct['ticket']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code'],
            'fully_paid_date': request.fully_paid_date,
        }
    )

    #######################################################################
    usermail_notgv_notbc_notransaction_subject = (
        u'C3S General Assembly & Barcamp 2016: your cancellation')
    if lang == "de":
        usermail_notgv_notbc_notransaction_subject = (
            'C3S Generalversammlung & Barcamp 2016: Deine Absage')
    usermail_notgv_notbc_notransaction = render(
        'templates/mails/usermail_notgv_notbc_notransaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'fully_paid_date': request.fully_paid_date,
        }
    )

    #######################################################################
    accmail_subject = u'[C3S_PT] neues ticket'
    accmail_body = render(
        'templates/mails/accmail.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'email': appstruct['ticket']['email'],
            'email_confirm_code': appstruct['email_confirm_code'],
            'gv_attendance': (
                appstruct['ticket']['ticket_gv'] == 1 or 'False'),
            'bc_attendance': (
                'attendance' in appstruct['ticket']['ticket_bc'] or 'False'),
            'bc_buffet': (
                'buffet' in appstruct['ticket']['ticket_bc'] or 'False'),
            'discount': appstruct['ticket']['discount'],
            'the_total': appstruct['ticket']['the_total'],
            'comment': appstruct['ticket']['comment'],
            'gv_representation': (
                appstruct['ticket']['ticket_gv'] == 2 or 'False'),
            'rep_firstname': appstruct['representation']['firstname'],
            'rep_lastname': appstruct['representation']['lastname'],
            'rep_email': appstruct['representation']['email'],
            'rep_street': appstruct['representation']['street'],
            'rep_zip': appstruct['representation']['zip'],
            'rep_city': appstruct['representation']['city'],
            'rep_country': appstruct['representation']['country'],
            'rep_type': appstruct['representation']['representation_type'],
            'tshirt': appstruct['ticket']['ticket_tshirt'] or 'False',
            # no shirts
            'tshirt_type': 0,
            'tshirt_size': 0,
            'supporter': (
                '1' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_l': (
                '2' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_xl': (
                '3' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_xxl': (
                '4' in appstruct['ticket']['ticket_support'] or 'False'),
        }
    )

    # ## send mails
    mailer = get_mailer(request)

    # ## pick usermail
    usermail_body = usermail_gv_transaction
    usermail_subject = usermail_gv_transaction_subject
    if (appstruct['ticket']['ticket_gv'] != 3):
        if (appstruct['ticket']['the_total'] == 0):
            usermail_body = usermail_gv_notransaction
            usermail_subject = usermail_gv_notransaction_subject
    else:
        if (appstruct['ticket']['ticket_bc']):
            usermail_body = usermail_notgv_bc
            usermail_subject = usermail_notgv_bc_subject
        else:
            if (appstruct['ticket']['the_total'] > 0):
                usermail_body = usermail_notgv_notbc_transaction
                usermail_subject = usermail_notgv_notbc_transaction_subject
            else:
                usermail_body = usermail_notgv_notbc_notransaction
                usermail_subject = usermail_notgv_notbc_notransaction_subject

    # ## pick usermail
    usermail_obj = Message(
        subject=usermail_subject,
        sender=request.registry.settings['c3spartyticketing.mail_sender'],
        recipients=[appstruct['ticket']['email']],
        body=usermail_body
    )

    if 'true' in request.registry.settings['testing.mail_to_console']:
        # ^^ yes, a little ugly, but works; it's a string
        # print "printing mail"
        print(usermail_body.encode('utf-8'))
    else:
        # print "sending mail"
        mailer.send(usermail_obj)

    # ## send accmail
    if 'true' in request.registry.settings['testing.mail_to_console']:
        print(accmail_body.encode('utf-8'))
    else:
        accmail_obj = Message(
            subject=accmail_subject,
            sender=request.registry.settings['c3spartyticketing.mail_sender'],
            recipients=[
                request.registry.settings['c3spartyticketing.mail_rec']],
            body=encrypt_with_gnupg(accmail_body.encode('utf-8'))
        )
        mailer.send(accmail_obj)

    # make the session go away
    request.session.invalidate()
    return {
        'firstname': appstruct['ticket']['firstname'],
        'lastname': appstruct['ticket']['lastname'],
        'transaction': (appstruct['ticket']['the_total'] > 0),
        'canceled': (appstruct['ticket']['ticket_gv'] == 3),
        'bc_attendance': appstruct['ticket']['ticket_bc']
    }


@view_config(route_name='finished', renderer='templates/finished.pt')
def finished_view(request):
    """
    Show the ticket readonly, e.g. if user has already submitted and
    finish_on_submit is on.

    Renderer:
        templates/finished.pt
    """

    # ## pick route
    route = check_route(request, 'finished')
    if isinstance(route, HTTPRedirection):
        return route

    # ## generate appstruct
    appstruct = ticket_appstruct(request, 'finished')

    # ## generate form
    schema = ticket_member_schema(request, appstruct, readonly=True)
    form = deform.Form(
        schema,
        buttons=[],
        # use_ajax=True,
        renderer=zpt_renderer
    )

    return {
        'readonlyform': form.render(
            appstruct=appstruct
        ),
        'token': request.session['userdata']['email_confirm_code']
    }


@view_config(route_name='end',
             renderer='templates/end.pt')
def end_view(request):
    """
    Show message after registration time is over.

    Renderer:
        templates/end.pt
    """
    # ## pick route
    today = datetime.today().date()
    registration_endgvonly = dateutil.parser.parse(
        request.registry.settings['registration.endgvonly']
    ).date()
    if today <= registration_endgvonly:
        return HTTPFound(location=request.route_url('party'))

    return {}
