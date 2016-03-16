# -*- coding: utf-8 -*-
"""
This module holds the main Ticket forms.

There are different Forms, depending on where the user comes from:

**C3S Members**
  have received an invitation email with a link (containing a **token**).
  This link triggers c3sPartyTicketing to ask relevant information
  via REST-API call from c3sMembership, so first and last name
  as well as membership type are known to c3sPartyTicketing.

**Nonmembers**
  who go to the ticketing site
  are presented with the non-member form.


As this module is very loooong, I'll try and list all defs and classes here:

def **ticket_member_schema**
    - def validator
    - class TicketData
    - class RegistrationData
    - class TicketForm

def **ticket_member_gvonly_schema**
    - def validator
    - class TicketGvonlyData
    - class RegistrationData
    - class TicketForm

def **ticket_member_nonmember_schema**
    - def validator
    - class TicketData
    - class RegistrationData
    - class TicketForm

def ticket_appstruct

def check_route

def load_user

def party_view

def confirm_view

def success_view

def finished_view

def end_view             # registration time is over

def nonmember_view              # nonmember-ticket (barcamp)

def nonmember_confirm_view      # nonmember-ticket (barcamp)

def nonmember_success_view      # nonmember-ticket (barcamp)

def nonmember_end_view          # nonmember-ticket (barcamp)

def get_ticket                  # produce PDF

def get_ticket_mobile           # produce smaller PDF
"""
from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
from c3spartyticketing.models import (
    DBSession,
    PartyTicket,
)
from c3spartyticketing.utils import make_random_string
from c3spartyticketing.ticket_member_schema import ticket_member_schema
from c3spartyticketing.ticket_nonmember_schema import ticket_nonmember_schema
from c3spartyticketing.ticket_member_gvonly_schema import (
    ticket_member_gvonly_schema)

from datetime import datetime
import dateutil.parser
import deform
from deform import ValidationFailure
import json
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

from pyramid.threadlocal import get_current_request
from pyramid.view import view_config
import requests
from requests import ConnectionError
# from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import (
    InvalidRequestError,
    IntegrityError
)

from pyramid.renderers import render

# from sets import Set

# from translationstring import TranslationStringFactory
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


def ticket_appstruct(request, view=''):
    '''
        Ensures the consistent creation of a valid ticket appstruct.
        Tries creation in the following order:

        1. Use from possibly edited session (reedit, refresh)
        2. If id not given, create new from userdata
        3. If id given, create from dbenty
        4. Redirect to access denied url
    '''
    print('--- creating appstruct ------------------------------------------')

    userdata = request.session['userdata']
    assert(userdata)
    print "userdata: {}".format(userdata)

    if 'appstruct' in request.session:
        # Use from possibly edited session (reedit, refresh).
        print('using session:')
        appstruct = request.session['appstruct']
        if appstruct is None:
            return HTTPFound(
                location=request.registry.settings[
                    'registration.access_denied_url'
                ]
            )
        print "-- appstruct: {}".format(appstruct)
        return appstruct

    userdata = request.session['userdata']
    if userdata['id'] is 'None':
        # If id not given, create new from userdata
        print("using userdata for new form.")
        appstruct = {
            'ticket': request.session['userdata']
        }
        print "-- appstruct: {}".format(appstruct)
        return appstruct

    # Create from dbenty
    assert(userdata['id'])
    _ticket = PartyTicket.get_by_id(userdata['id'])
    assert isinstance(_ticket, PartyTicket)
    print "using dbentry (id {}):".format(userdata['id'])
    appstruct = {
        'ticket': {
            'ticket_gv': _ticket.ticket_gv_attendance,
            'ticket_bc': [
                'attendance',
                'buffet'
            ],
            # 'ticket_all': _ticket.ticket_all,
            'ticket_all': False,
            'ticket_support': [
                '1',
                '2',
                '3',
                '4',
            ],
            'support': _ticket.support,
            'the_total': _ticket.the_total,
            'comment': _ticket.user_comment,
            'ticket_tshirt': _ticket.ticket_tshirt,
            'firstname': _ticket.firstname,
            'lastname': _ticket.lastname,
            'token': _ticket.token,
            'email': _ticket.email,
            '_LOCALE_': _ticket.locale
        },
        'representation': {
            'firstname': _ticket.rep_firstname,
            'lastname': _ticket.rep_lastname,
            'email': _ticket.rep_email,
            'street': _ticket.rep_street,
            'zip': _ticket.rep_zip,
            'city': _ticket.rep_city,
            'country': _ticket.rep_country,
            'representation_type': _ticket.rep_type
        },
        # 'tshirt': {
        #    'tshirt_type': _ticket.ticket_tshirt_type,
        #    'tshirt_size': _ticket.ticket_tshirt_size
        # }
    }
    if not _ticket.ticket_bc_attendance:
        appstruct['ticket']['ticket_bc'].remove('attendance')
    if not _ticket.ticket_bc_buffet:
        appstruct['ticket']['ticket_bc'].remove('buffet')
    if not _ticket.ticket_support:
        appstruct['ticket']['ticket_support'].remove('1')
    if not _ticket.ticket_support_l:
        appstruct['ticket']['ticket_support'].remove('2')
    if not _ticket.ticket_support_xl:
        appstruct['ticket']['ticket_support'].remove('3')
    if not _ticket.ticket_support_xxl:
        appstruct['ticket']['ticket_support'].remove('4')

    print "-- appstruct: {}".format(appstruct)
    return appstruct


def check_route(request, view=''):
    '''
        A. This function performs checks:
            1.  *userdata* check:
                *userdata* has to be set in *load_user*.
                *load_user()* is the only entrance door.
                If *userdata* is not set,
                redirect to access denied url

            3.  dbentry check:
                If *finish_on_submit* is active and user has already submitted,
                redirect to finished view

            4.  date check:
                If registration period is over,
                redirect to finished view

        B. individual routes:
            redirects based on keywords in POST
    '''
    print('--- pick route --------------------------------------------------')
    if view:
        print('called from view: %s') % view

    # ## checks

    # userdata check:
    if 'userdata' in request.session:
        userdata = request.session['userdata']
        try:
            assert('token' in userdata)
            assert('id' in userdata)
            assert('firstname' in userdata)
            assert('lastname' in userdata)
            assert('email' in userdata)
            assert('mtype' in userdata)
        except:
            print('userdata test: user not found. redirecting...')
            return HTTPFound(
                location=request.registry.settings[
                    'registration.access_denied_url']
            )
    else:
        print('userdata test: user not found. redirecting...')
        return HTTPFound(
            location=request.registry.settings[
                'registration.access_denied_url']
        )

    # dbentry check:
    if view is not 'finished' and view is not 'confirm':
        if 'true' in request.registry.settings[
                'registration.finish_on_submit']:
            if PartyTicket.has_token(userdata['token']):
                print('dbentry check: ticket already exists. redirecting...')
                return HTTPFound(location=request.route_url('finished'))
            else:
                print('token check: ticket does not exist')
        else:
            print('token check: deactivated')

    # date check:
    if view is not 'finished':
        today = datetime.today().date()
        registration_endgvonly = dateutil.parser.parse(
            request.registry.settings['registration.endgvonly']
        ).date()
        if today > registration_endgvonly:
            print('date check: registration is finished. redirecting ...')
            # if ticket was already submitted, show finished ticket
            if PartyTicket.has_token(userdata['token']):
                return HTTPFound(location=request.route_url('finished'))
            # else show userfeedback: registration has ended
            return HTTPFound(location=request.route_url('end'))
        else:
            print('date check: registration is still possible')

    # ## individual routes

    # confirm view:
    if view is 'confirm':

        if 'appstruct' not in request.session:
            return HTTPFound(location=request.route_url('party'))

        # reedit: user wants to re-edit her data
        if 'reedit' in request.POST:
            return HTTPFound(location=request.route_url('party')+'?reedit')

        # order: user wants to confirm the data
        if 'confirm' in request.POST:
            return

        # order: user confirmed the data
        if 'confirmed' in request.POST:
            request.session['flags'] = {
                'confirmed': True
            }
            return HTTPFound(location=request.route_url('success'))

    # success view:
    if view is 'success':

        # confirmed: test flag
        if (
                'flags' not in request.session or
                'confirmed' not in request.session['flags']):
            return HTTPFound(location=request.route_url('party'))

        if 'appstruct' not in request.session:
            return HTTPFound(location=request.route_url('party'))

    # finished view:
    if view is 'finished':

        # check if db entry exists
        if not PartyTicket.has_token(userdata['token']):
            return HTTPFound(location=request.route_url('party'))
        return
    return


@view_config(route_name='load_user')
def load_user(request):
    '''
    A view for all members with invitation link from invitation email.

    Receive link containing **token** and load user details.

    Saves details in userdata.

    Userdata should only be changed in this view.

    *load_user* is the only entrance door.
    '''
    print('--- load user ---------------------------------------------------')

    _token = request.matchdict['token']
    _email = request.matchdict['email']

    # ## clear session
    request.session['userdata'] = {}
    request.session['derivedvalues'] = {}
    request.session['flags'] = {}
    # XXX think about a nicer abstract way to save derived values (->form
    # object) and flags, which control the flow

    # distinction member / nonmember
    request.session['flags']['isMember'] = True

    # ## load userdata from dbentry
    _ticket = PartyTicket.get_by_token(_token)
    print('searching db for user ...')
    try:
        if isinstance(_ticket, PartyTicket):
            assert(_ticket.token == _token)
            assert(_ticket.email == _email)
            print "found a valid dbentry (id: {})".format(_ticket.id)
            userdata = {
                'token': _ticket.token,
                'id': _ticket.id,
                'firstname': _ticket.firstname,
                'lastname': _ticket.lastname,
                'email': _ticket.email,
                'mtype': _ticket.membership_type,
                'is_legalentity': _ticket.is_legalentity,
                'email_confirm_code': _ticket.email_confirm_code
            }
            request.session['userdata'] = userdata
            return HTTPFound(location=request.route_url('party'))
    except:
        print "no valid dbentry found."
        pass

    # ## load userdata from membership app
    data = json.dumps({"token": _token})
    # print(data)
    try:
        print('querying MGV API ...')
        _auth_header = {
            'X-Messaging-Token': request.registry.settings['yes_auth_token']
        }
        res = requests.put(
            request.registry.settings['yes_api_url'],
            data,
            headers=_auth_header,
        )
    except ConnectionError, ce:
        print("we hit a ConnectionError. report to staff immediately!")
        mailer = get_mailer(request)
        message_to_staff = Message(
            subject="[ALERT] c3sPartyTicketing reports ConnectionError!",
            sender=request.registry.settings['c3spartyticketing.mail_sender'],
            recipients=[
                request.registry.settings['c3spartyticketing.mail_rec']],
            body="""{}

                 """.format(ce)
        )
        if 'true' in request.registry.settings['testing.mail_to_console']:
            # ^^ yes, a little ugly, but works; it's a string
            # print "printing mail"
            print(
                message_to_staff.subject,
                message_to_staff.body,
            )
        else:
            # print "sending mail"
            mailer.send(message_to_staff)

        request.session.flash(
            """Sorry, there was a problem loading your data from the membership registry.
            We notified staff about this.
            """,
            'message_to_user'
        )
        return HTTPFound(request.route_url('error_page'))

    # print u"the result: {}".format(res)
    # print u"the result.json(): {}".format(res.json())
    # print u"the result.reason: {}".format(res.reason)
    # print u"dir(res): {}".format(dir(res))
    try:
        userdata = {
            'token': _token,
            'id': 'None',
            'firstname': res.json()['firstname'],
            'lastname': res.json()['lastname'],
            'email': res.json()['email'],
            'mtype': res.json()['mtype'],
            'is_legalentity': res.json()['is_legalentity'],
        }
        assert(res.json()['email'] == _email)
        request.session['userdata'] = userdata
        return HTTPFound(location=request.route_url('party'))
    except:
        print('no valid entry found. redirecting ...')
        pass

    return HTTPFound(
        location=request.registry.settings['registration.access_denied_url']
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
            'ticket_bc_attendance': 15,
            'ticket_bc_buffet': 12,
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
            1: 5,
            2: 10,
            3: 100
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
        ticket.ticket_support = (
            '1' in appstruct['ticket']['ticket_support']
        )
        ticket.ticket_support_x = (
            '2' in appstruct['ticket']['ticket_support']
        )
        ticket.ticket_support_xl = (
            '3' in appstruct['ticket']['ticket_support']
        )
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
            password='',  # appstruct['person']['password'],
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
            ticket_support=('1' in appstruct['ticket']['ticket_support']),
            ticket_support_x=(
                '2' in appstruct['ticket']['ticket_support']),
            ticket_support_xl=(
                '3' in appstruct['ticket']['ticket_support']),
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
            'supporter_x': (
                '2' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_xl': (
                '3' in appstruct['ticket']['ticket_support'] or 'False')
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
    from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
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
                'formerror': True
            }

        # ## derived values

        # map option to price
        the_values = {
            'ticket_bc_attendance': 15,
            'ticket_bc_buffet': 12,
            'ticket_tshirt': 0,
            'ticket_all': 42,
        }

        # map supporter tickets to price
        the_support = {
            1: 5,
            2: 10,
            3: 100
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
        ticket_support_x=(
            '2' in appstruct['ticket']['ticket_support']),
        ticket_support_xl=(
            '3' in appstruct['ticket']['ticket_support']),
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
    usermail_nonmember_subject = \
        u'C3S Barcamp 2016: your order'
    if lang == "de":
        usermail_nonmember_subject = \
            'C3S Barcamp 2016: Deine Bestellung'
    usermail_nonmember = render(
        'templates/mails/usermail_nonmember-'+lang+'.pt',
        {
            'firstname': appstruct['personal']['firstname'],
            'lastname': appstruct['personal']['lastname'],
            'the_total': request.session['derivedvalues']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code']
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
            'supporter_x': (
                '2' in appstruct['ticket']['ticket_support'] or 'False'),
            'supporter_xl': (
                '3' in appstruct['ticket']['ticket_support'] or 'False')
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
