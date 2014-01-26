# -*- coding: utf-8 -*-
import json
from c3spartyticketing.models import (
    PartyTicket,
    C3sStaff,
    DBSession,
)
from c3spartyticketing.utils import make_random_string
#from pkg_resources import resource_filename
import colander
import deform
from deform import ValidationFailure

#from pyramid.i18n import (
#    get_localizer,
#)
from pyramid.request import Request
from pyramid.view import view_config
#from pyramid.threadlocal import get_current_request
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    #forget,
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
    This view lets cachiers make/issue new tickets

    a form permits checkin of people, up to the amount of tickets
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
        #try:
        dbsession = DBSession()
        _new.payment_received = True
        #import pdb
        #pdb.set_trace()
        _new.checked_persons = int(_num)
        _new.payment_received_date = datetime.now()
        _new.email_confirm_code = 'CASHDESK' + make_random_string()
        _new.accountant_comment = 'issued by %s' % logged_in
        dbsession.add(_new)

        #except:
        #    print("new_ticket: something went wrong")
            #pass
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
    This view lets cachiers log in people

    a form permits checkin of people, up to the amount of tickets
    """
    logged_in = authenticated_userid(request)
    print("authenticated_userid: " + str(logged_in))
    log.info("check in conducted by %s" % logged_in)

    # check for input from checkin function POST
    #print(request.POST)
    # MultiDict([('persons', u'10'),
    #            ('checkin', u'Check in!'),
    #            ('code', u'ABCDEFGHIJ')])
    __check = ('checkin' in request.POST)
    __code = ('code' in request.POST)
    __personen = ('persons' in request.POST)
    if __check and __code and __personen:
        #print("############# check_in_cond is True.")
        _code = request.POST['code']
        _persons = request.POST['persons']
        _ticket = PartyTicket.get_by_code(_code)
        if isinstance(_ticket, NoneType):
            "if the ticket code was not found, return to base"
            request.session.flash('code not found. gleis 16 gibt es nicht.')
            return HTTPFound(
                location=request.route_url('kasse'))
        _ticket.checkin_time = datetime.now()
        #_ticket.checkin_seen = True
        _ticket.checked_persons += int(_persons)

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
            'paid': 'Nein'
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

    # types of tickets displayed in the backend
    ticket_type_options = {
        1: _(u'2. Klasse'),
        2: _(u'2. Klasse + Speisewagen'),
        3: _(u'1. Klasse'),
        4: _(u'Grüne Mamba'),
    }

    _klass = ticket_type_options.get(_ticket.ticket_type)
    _num_passengers = PartyTicket.num_passengers()
    _num_open_tickets = int(
        PartyTicket.get_num_tickets()) - int(_num_passengers)
    _vacancies = _ticket.num_tickets - _ticket.checked_persons

    return {
        'vacancies': _vacancies,  # the free tickets of this visitor
        'logged_in': logged_in,
        'num_passengers': _num_passengers,
        'num_open_tickets': _num_open_tickets,
        'code': _code,
        'klass': _klass,
        'paid': _ticket.payment_received,
        'ticket': _ticket,
    }


@view_config(renderer='templates/kasse.pt',
             permission='cashdesk',
             route_name='kasse')
def kasse(request):
    """
    This view lets cachiers do stuff
    """
    logged_in = authenticated_userid(request)
    print("authenticated_userid: " + str(logged_in))
    #log.info("check in conducted by %s" % logged_in)

    # check for input from "find dataset by confirm code" form
    if 'code_to_show' in request.POST:
        print("found code_to_show in POST: %s" % request.POST['code_to_show'])
        try:
            _code = request.POST['code_to_show']
            #print(_code)
            _entry = PartyTicket.get_by_code(_code)
            print(_entry)
            print(_entry.id)

            return HTTPFound(
                location=request.route_url(
                    'check_in',
                    event='p1402',
                    code=_entry.email_confirm_code)
            )
        except:
            # choose default
            print("barf!")
            request.session.flash('gleis 16 gibt es garnicht!')
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
        #use_ajax=True,  # <-- whoa!
        #renderer=zpt_renderer,
    )
    autoformhtml = form.render()

    _num_passengers = PartyTicket.num_passengers()
    _num_open_tickets = int(
        PartyTicket.get_num_tickets()) - int(_num_passengers)

    return {
        'autoform': autoformhtml,
        'logged_in': logged_in,
        'num_passengers': _num_passengers,
        'num_open_tickets': _num_open_tickets
    }


@view_config(renderer='templates/login.pt',
             route_name='k')
def cashiers_login(request):
    """
    This view lets cashiers log in
    """
    logged_in = authenticated_userid(request)
    #print("authenticated_userid: " + str(logged_in))

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
            title=_(u"login"),
            oid="login",
        )
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.PasswordWidget(size=20),
            title=_(u"password"),
            oid="password",
        )

    schema = CashiersLogin()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        #print("the form was submitted")
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
