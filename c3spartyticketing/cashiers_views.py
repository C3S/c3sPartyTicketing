# -*- coding: utf-8 -*-
"""
This module holds functionality needed at the cashdesk of venues.


"""
import json
from c3spartyticketing.models import (
    PartyTicket,
    C3sStaff,
    DBSession,
)
from c3spartyticketing.utils import make_random_string
# from pkg_resources import resource_filename
import colander
import deform
from deform import ValidationFailure

# from pyramid.i18n import (
#    get_localizer,
# )
from pyramid.request import Request
from pyramid.view import (
    view_config,
    forbidden_view_config
)
# from pyramid.threadlocal import get_current_request
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    # forget,
    authenticated_userid,
)
from pyramid.url import route_url
from translationstring import TranslationStringFactory
from types import NoneType
from datetime import datetime

_ = TranslationStringFactory('c3spartyticketing')

DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/new_ticket.pt',
             permission='cashdesk',
             route_name='new_ticket')
def new_ticket(request):
    """
    This view lets cachiers make/issue new tickets.
    We used this form during the HQ inauguration party for bookkeeping,
    as we had to count how many people were in the building.

    === ============================
    URL http/s://app:port/new_ticket
    === ============================

    Returns:
       | a form permits issuing tickets for people
       | rendered to **templates/new_ticket.pt**
    """
    logged_in = authenticated_userid(request)
    print("authenticated_userid: " + str(logged_in))

    print("the request.POST: %s" % request.POST)
    add_cond = ('persons' in request.POST)
    if add_cond:
        _num = request.POST['persons']
        if 'type1' in request.POST:
            _type = request.POST['type1']
            _type_int = 1
            _type_cost = 5
        elif 'type2' in request.POST:
            _type = request.POST['type2']
            _type_int = 2
            _type_cost = 15
        elif 'type3' in request.POST:
            _type = request.POST['type3']
            _type_int = 3
            _type_cost = 50
        elif 'type4' in request.POST:
            _type = request.POST['type4']
            _type_int = 4
            _type_cost = 100
        log.info(
            "%s tickets(s) of cat. %s sold by %s" % (_num, _type, logged_in))
        _new = PartyTicket(
            firstname='anon',
            lastname='anon',
            email='anon',
            password='None',
            locale='de',
            email_is_confirmed=False,
            email_confirm_code='cash',
            num_tickets=int(_num),
            ticket_type=_type_int,
            the_total=int(_num)*_type_cost,
            user_comment='got ticket at entry',
            date_of_submission=datetime.now(),
            payment_received=True
        )
        dbsession = DBSession()
        _new.payment_received = True
        _new.checked_persons = int(_num)
        _new.payment_received_date = datetime.now()
        _new.email_confirm_code = 'CASHDESK' + make_random_string()
        _new.accountant_comment = 'issued by %s' % logged_in
        dbsession.add(_new)

    _num_passengers = PartyTicket.num_passengers()
    _num_open_tickets = int(
        PartyTicket.get_num_tickets()) - int(_num_passengers)

    return {
        'logged_in': logged_in,
        'num_passengers': _num_passengers,
        'num_open_tickets': _num_open_tickets,
    }


@view_config(renderer='templates/check_in.pt',
             permission='cashdesk',
             route_name='check_in')
def check_in(request):
    """
    This view lets cashiers check-in people at the actual event.

    === ======================================
    URL http/s://app:port/ci/ga4bc/EXAMPLECODE
    === ======================================


    Returns:
       | a form permitting checkin of people,
       | up to the amount of person on this ticket.
    """
    logged_in = authenticated_userid(request)
    # print("authenticated_userid: " + str(logged_in))
    log.info("check in conducted by %s" % logged_in)

    # check for input from checkin function POST
    # print(request.POST)
    # MultiDict([('persons', u'10'),
    #            ('checkin', u'Check in!'),
    #            ('code', u'ABCDEFGHIJ')])
    __check_bc = ('checked_bc' in request.POST)
    __check_gv = ('checked_gv' in request.POST)
    __received_extra1 = ('received_extra1' in request.POST)
    __received_extra2 = ('received_extra2' in request.POST)
    __code = ('code' in request.POST)
    # __personen = ('persons' in request.POST)

    if __check_bc and __code:
        _code = request.POST['code']
        # _persons = request.POST['persons']
        _ticket = PartyTicket.get_by_code(_code)
        if isinstance(_ticket, NoneType):
            "if the ticket code was not found, return to base"
            request.session.flash('code not found.')
            return HTTPFound(
                location=request.route_url('kasse'))
        if _ticket.ticket_bc_attendance:
            _ticket.checked_bc = True
            _ticket.checked_bc_time = datetime.now()
            # _ticket.checkin_seen = True
            # _ticket.checked_persons += int(_persons)

    if __check_gv and __code:
        _code = request.POST['code']
        # _persons = request.POST['persons']
        _ticket = PartyTicket.get_by_code(_code)
        if isinstance(_ticket, NoneType):
            "if the ticket code was not found, return to base"
            request.session.flash('code not found.')
            return HTTPFound(
                location=request.route_url('kasse'))
        if _ticket.ticket_gv_attendance == 1:
            _ticket.checked_gv = True
            _ticket.checked_gv_time = datetime.now()
        # _ticket.checkin_seen = True
        # _ticket.checked_persons += int(_persons)

    if __received_extra1 and __code:
        _code = request.POST['code']
        # _persons = request.POST['persons']
        _ticket = PartyTicket.get_by_code(_code)
        if isinstance(_ticket, NoneType):
            "if the ticket code was not found, return to base"
            request.session.flash('code not found.')
            return HTTPFound(
                location=request.route_url('kasse'))
        _ticket.received_extra1 = True
        _ticket.received_extra1_time = datetime.now()
        # _ticket.checkin_seen = True
        # _ticket.checked_persons += int(_persons)

    if __received_extra2 and __code:
        _code = request.POST['code']
        # _persons = request.POST['persons']
        _ticket = PartyTicket.get_by_code(_code)
        if isinstance(_ticket, NoneType):
            "if the ticket code was not found, return to base"
            request.session.flash('code not found.')
            return HTTPFound(
                location=request.route_url('kasse'))
        _ticket.received_extra2 = True
        _ticket.received_extra2_time = datetime.now()
        # _ticket.checkin_seen = True
        # _ticket.checked_persons += int(_persons)

    '''
    checkin was called from a prepared URL ('/ci/{event}/{code}')
    '''
    _code = request.matchdict['code']
    # get dataset from db
    _ticket = PartyTicket.get_by_code(_code)
    if isinstance(_ticket, NoneType):  # not found
        print("ticket not found!?!")
        return {
            'logged_in': logged_in,
            'status': 'NOT FOUND',
            'code': '',
            'paid': 'Nein',
            'stats': PartyTicket.stats_cashiers()
        }
    else:
        print("the ticket: %s" % _ticket)
        pass

    '''
    users may pay at the counter,
    if they forgot to transfer (and room is not full)
    '''
    if 'Bezahlt' in request.POST:
        _ticket.payment_received = True
        _ticket.payment_received_date = datetime.now()

    if 'comment' in request.POST:
        _comment = request.POST['cashier_comment']
        _ticket.cashiers_comment = (_ticket.cashiers_comment or u'') \
            + '\r\n\r\n' \
            + '-'*80 \
            + '\r\n' \
            + str(datetime.now()) + ' | ' + str(request.user.login) + ':' \
            + '\r\n\r\n' \
            + unicode(_comment)

    # types of tickets displayed in the backend
    ticket_type_options = {
        ('ticket_gv', u'Attendance General Assembly'),
        ('ticket_bc', u'Attendance BarCamp'),
        ('ticket_bc_buffet', u'Buffet Barcamp'),
        ('ticket_tshirt', u'T-shirt'),
        ('ticket_all', u'All-Inclusive')
    }

    _ticket_rep1 = None
    if _ticket.represents_id1:
        _ticket_rep1 = PartyTicket.get_by_id(int(_ticket.represents_id1))
    _ticket_rep2 = None
    if _ticket.represents_id2:
        _ticket_rep2 = PartyTicket.get_by_id(int(_ticket.represents_id2))
    _paid = (1 if _ticket.payment_received or _ticket.the_total == 0 else 0)

    return {
        # 'vacancies': _vacancies,  # the free tickets of this visitor
        'logged_in': logged_in,
        'code': _code,
        'paid': _paid,
        'ticket': _ticket,
        'ticket_rep1': _ticket_rep1,
        'ticket_rep2': _ticket_rep2,
        'stats': PartyTicket.stats_cashiers(),
        'cashiers_comment': _ticket.cashiers_comment
    }


@forbidden_view_config()
def kasse_forbidden(request):
    return HTTPFound(location=request.route_url('k'))


@view_config(renderer='templates/kasse.pt',
             permission='cashdesk',
             route_name='kasse')
def kasse(request):
    """
    This view lets cachiers be cashiers:

    * Search for tickets using the code in an autocomplete form.
    * Display a statisitc about tickets checked in or pending.
    * Display information about code prefix and suffix.

    === =======================
    URL http/s://app:port/kasse
    === =======================

    Returns:
       | a) a form, statistics, useful information, rendered to a template;
       | b) if a valid code was submitted, redirect to check-in for ticket.
    """
    logged_in = authenticated_userid(request)
    # print("authenticated_userid: " + str(logged_in))
    # log.info("check in conducted by %s" % logged_in)

    # check for input from "find dataset by confirm code" form
    if 'code_to_show' in request.POST:
        print("found code_to_show in POST: %s" % request.POST['code_to_show'])
        try:
            _code = request.POST['code_to_show']
            # print(_code)
            _entry = PartyTicket.get_by_code(_code)
            print(_entry)
            print(_entry.id)

            return HTTPFound(
                location=request.route_url(
                    'check_in',
                    event=request.registry.settings['eventcode'],
                    code=_entry.email_confirm_code)
            )
        except:
            # choose default
            print("barf!")
            request.session.flash('Ticket nicht gefunden.')
            pass

    # prepare the autocomplete form with codes
    # get codes from another view via subrequest, see
    # http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/subrequest.html
    subreq = Request.blank('/all_codes')  # see http://0.0.0.0:6543/all_codes
    response = request.invoke_subrequest(subreq)
    the_codes = json.loads(response.body)  # gotcha: json needed!

    my_autoc_wid = deform.widget.AutocompleteInputWidget(
        min_length=1,
        title="widget title",
        values=the_codes,
    )

    # prepare a form for autocomplete search for codes.
    class CodeAutocompleteForm(colander.MappingSchema):
        """
        colander schema to make deform autocomplete form
        """
        code_to_show = colander.SchemaNode(
            colander.String(),
            title="Code eingeben (autocomplete)",
            validator=colander.Length(min=1, max=8),
            widget=my_autoc_wid,
            description='start typing. use arrows. press enter. twice.'

        )

    schema = CodeAutocompleteForm()
    form = deform.Form(
        schema,
        buttons=('go!',),
        # use_ajax=True,  # <-- whoa!
        # renderer=zpt_renderer,
    )
    autoformhtml = form.render()

    return {
        'autoform': autoformhtml,
        'logged_in': logged_in,
        'stats': PartyTicket.stats_cashiers()
    }


@view_config(renderer='templates/login.pt',
             route_name='k')
def cashiers_login(request):
    """
    This view lets cashiers log in.

    The view shows a form to enter login and password.
    If a person is logged in and belongs to group 'kasse' or 'staff'
    she is redirected to the cashiers desk/check_in

    === ===================
    URL http/s://app:port/k
    === ===================
    """
    logged_in = authenticated_userid(request)
    # print("authenticated_userid: " + str(logged_in))

    log.info("login by %s" % logged_in)

    if logged_in is not None:  # if user is already authenticated
        return HTTPFound(  # redirect her to the dashboard
            request.route_url('kasse',))

    class CashiersLogin(colander.MappingSchema):
        """
        colander schema for login form
        """
        login = colander.SchemaNode(
            colander.String(),
            title=u"login",
            oid="login",
        )
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.PasswordWidget(size=20),
            title=u"password",
            oid="password",
        )

    schema = CashiersLogin()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', u'Submit'),
            deform.Button('reset', u'Reset')
        ],
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        # print("the form was submitted")
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            print(e)

            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # get user and check pw...
        login = appstruct['login']
        password = appstruct['password']

        try:
            checked = C3sStaff.check_password(login, password)
        except AttributeError:  # pragma: no cover
            checked = False
        if checked:
            log.info("password check for %s: good!" % login)
            headers = remember(request, login)
            log.info("logging in %s" % login)
            return HTTPFound(  # redirect to accountants dashboard
                location=route_url(  # after successful login
                    'kasse',
                    request=request),
                headers=headers)
        else:
            log.info("password check: failed.")

    html = form.render()
    return {'form': html, }
