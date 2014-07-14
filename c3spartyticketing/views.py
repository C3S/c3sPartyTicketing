# -*- coding: utf-8 -*-

from c3spartyticketing.models import (
    DBSession,
    PartyTicket,
)
from c3spartyticketing.utils import (
    make_qr_code_pdf,
    make_qr_code_pdf_mobile,
    make_random_string,
)

import colander
from datetime import datetime
import deform
from deform import ValidationFailure
import json
from pkg_resources import resource_filename

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import (
    TranslationStringFactory,
    get_localizer,
    get_locale_name,
)
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.response import Response
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config
import requests
#from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import (
    InvalidRequestError,
    IntegrityError
)
from types import NoneType
#from translationstring import TranslationStringFactory
_ = TranslationStringFactory('c3spartyticketing')

from sets import Set

#deform_templates = resource_filename('deform', 'templates')

#c3spartyticketing_templates = resource_filename(
#    'c3spartyticketing', 'templates')

#my_search_path = (deform_templates, c3spartyticketing_templates)


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

def ticket_schema(request, appstruct, readonly=False):

    ### validator

    def validator(form, value):
        #print("the value from the validator: %s \n") % value
        #for thing in value:
        #    print(u"the thing: %s") % thing
        #    print(u"type: %s") % type(thing)
        #print("the form from the validator: %s \n") % form
        #for thing in form:
        #    print(u"the thing: %s") % thing
        #    print(u"type: %s") % type(thing)
        #    for thing2 in thing:
        #        print(u"  the thing2: %s") % thing2
        #        print(u"  type2: %s") % type(thing2)

        # 2DO: herausfinden, wie man per klassenvalidator colander.Invalid ansprechen muss,
        #      damit deform den error am richtigen ort platziert und die richtigen klassen vergibt
        exc = colander.Invalid(form)
        if value['ticket']['ticket_tshirt']:
            if not value['tshirt']['tshirt_type']:           
                exc['tshirt'] = "Der Schnitt des T-Shirts muss angegeben werden."
                raise exc
            if not value['tshirt']['tshirt_size']:
                exc['tshirt'] = "Die Größe des T-Shirts muss angegeben werden."
                raise exc
        if value['ticket']['ticket_gv'] == 2:
            if not value['representation']['firstname']:
                exc['representation'] = "Der Vorname des/r Bevollmächtigten muss angegeben werden."
                raise exc
            if not value['representation']['lastname']:
                exc['representation'] = "Der Nachname des/r Bevollmächtigten muss angegeben werden."
                raise exc
            if not value['representation']['street']:
                exc['representation'] = "Die Straße des/r Bevollmächtigten muss angegeben werden."
                raise exc
            if not value['representation']['zip']:
                exc['representation'] = "Die Plz des/r Bevollmächtigten muss angegeben werden."
                raise exc
            if not value['representation']['city']:
                exc['representation'] = "Die Stadt des/r Bevollmächtigten muss angegeben werden."
                raise exc
            if not value['representation']['country']:
                exc['representation'] = "Das Land des/r Bevollmächtigten muss angegeben werden."
                raise exc
            if not value['representation']['representation_type']:
                exc['representation'] = "Die Beziehung zu dem/r Bevollmächtigten muss angegeben werden."
                raise exc

    ### deferred

    @colander.deferred
    def deferred_missing_firstname(node, kw):
        try:
            return request.session['appstruct_preset']['firstname']
        except:
            return 'foo'

    @colander.deferred
    def deferred_missing_lastname(node, kw):
        try:
            return request.session['appstruct_preset']['lastname']
        except:
            return 'bar'

    @colander.deferred
    def deferred_missing_email(node, kw):
        try:
            return request.session['appstruct_preset']['email']
        except:
            return 'moo'

    @colander.deferred
    def deferred_missing_token(node, kw):
        try:
            return request.session['appstruct_preset']['token']
        except:
            return 'boo'

    ### options
    
    ticket_gv_options = (
        (1, _(u'Ich werde an der Generalversammlung teilnehmen')),
        (2, _(u'Ich werde an der Generalversammlung nicht persönlich teilnehmen, sondern lasse mich vertreten')),
        (3, _(u'Ich werde an der Generalversammlung nicht teilnehmen'))
    )

    ticket_bc_options = (
        ('attendance', _(u'I will attend the BarCamp (€9)')),
        ('buffet', _(u'I\'d like to dine from the BarCamp buffet (€8,50)'))
    )

    rep_type_options = (
        ('member', _(u'Mitglied der Genossenschaft')),
        ('partner', _(u'mein Ehefrau/mein Ehemann')),
        ('parent', _(u'meine Mutter/mein Vater')),
        ('child', _(u'meine Tochter/mein Sohn')),
        ('sibling', _(u'meine Schwester/mein Bruder'))
    )

    tshirt_type_options = (
        ('m', _(u'male')),
        ('f', _(u'female'))
    )

    tshirt_size_options = (
        ('S', _(u'S')),
        ('M', _(u'M')),
        ('L', _(u'L')),
        ('XL', _(u'XL')),
        ('XXL', _(u'XXL')),
        ('XXXL', _(u'XXXL'))
    )

    ### formparts

    class TicketData(colander.MappingSchema):

        locale_name = get_locale_name(request)
        ticket_gv = colander.SchemaNode(
            colander.Integer(),
            title=_(u"Generalversammlung:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_gv_options,
                readonly=readonly
            ),
            oid="ticket_gv"
        )
        ticket_bc = colander.SchemaNode(
            colander.Set(),
            title=_(u"Barcamp:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_bc_options,
                readonly=readonly
            ),
            missing='',
            description=_(
                u'The buffet consists of e.g., salads, vegetables, dips, '
                u'chese and meat platters. A free drink is included.'),
            oid="ticket_bc"
        )
        if readonly:
            ticket_bc.description = None
            if not appstruct['ticket']['ticket_bc']:
                ticket_bc = None
        ticket_tshirt = colander.SchemaNode(
            colander.Boolean(),
            title=_(u"Extras:"),
            widget=deform.widget.CheckboxWidget(
                readonly=readonly,
                readonly_template='forms/checkbox_label.pt'
            ),
            label="T-Shirt (€25)",
            missing='',
            description=_(
                u'There will be one joint T-shirt design for both events in C3S green, '
                u'black and white. Exclusively for participants, available only if pre-ordered! '
                u'You can collect your pre-ordered T-shirt at both the BarCamp '
                u'and the general assembly.'),
            oid="ticket_tshirt"
        )
        if readonly:
            ticket_tshirt.description = None
            if not appstruct['ticket']['ticket_tshirt']:
                ticket_tshirt = None                
        ticket_all = colander.SchemaNode(
            colander.Boolean(),
            title=_(u"Special Offer:"),
            widget=deform.widget.CheckboxWidget(
                readonly=readonly,
                readonly_template='forms/checkbox_label.pt'
            ),
            label="All-Inclusive-Paket (€40)",
            missing='',
            description=_(
                u'The all-inclusive package covers the participation in the BarCamp '
                u'(including buffet and free drink), participation in the general '
                u'assembly, and the exclusive event T-shirt as well.'),
            oid="ticket_all"
        )
        if readonly:
            ticket_all.description = None
            ticket_all.label = "All-Inclusive-Paket Rabatt (-€2,50)"
            if not appstruct['ticket']['ticket_all']:
                ticket_all = None
        if readonly and appstruct['ticket']['the_total'] > 0:
            the_total = colander.SchemaNode(
                colander.Decimal(quant='1.00'),
                widget=deform.widget.TextInputWidget(
                    readonly=readonly,
                    readonly_template="forms/textinput_money.pt",
                ),
                title=_(u"Gesamtbetrag"),
                description=_(
                    u'Deine Bestellung muss spätestens bis zum 18.08.2014 vollständig bezahlt sein '
                    u'(Zahlungseingang auf unserem Konto). '
                    u'Andernfalls müssen wir die gesamte Bestellung stornieren. '
                    u'Die Zahlung erfolgt ausschließlich per Banküberweisung. '
                    u'Die Zahlungsinformationen werden dir per Email zugeschickt.'),
                oid="the-total",
            )
        comment = colander.SchemaNode(
            colander.String(),
            title=_("Kommentare"),
            missing='',
            validator=colander.Length(max=250),
            widget=deform.widget.TextAreaWidget(
                rows=3, cols=50,
                readonly=readonly
            ),
            description=_(u"Raum für Kommentare (255 Zeichen)"),
            oid="comment",
        )
        if readonly:
            comment.description = None
            if not appstruct['ticket']['comment']:
                comment = None
        # hidden fields for personal data
        token = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['appstruct_preset']['token'],
            missing=deferred_missing_token,
            oid="firstname",
        )
        firstname = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['appstruct_preset']['firstname'],
            missing=deferred_missing_firstname,
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['appstruct_preset']['lastname'],
            missing=deferred_missing_lastname,
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['appstruct_preset']['email'],
            missing=deferred_missing_email,
            oid="email",
        )
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=locale_name
        )

    class RepresentationData(colander.MappingSchema):
        """
        colander schema of respresentation form
        """
        note_top = colander.SchemaNode(
            colander.String(),
            title='',
            widget=deform.widget.TextInputWidget(
                readonly=True,
                readonly_template="forms/textinput_htmlrendered.pt"
            ),
            default=u'''
<p>Wir brauchen von Dir folgende Daten de(s/r) Bevollmächtigten:</p>
''',
            missing='',
            oid='rep-note'
        )
        note_top.missing=note_top.default # otherwise empty on redit
        if readonly:
            note_top = None
        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"Vorname"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"Nachname"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-lastname",
        )
        street = colander.SchemaNode(
            colander.String(),
            title=_(u'Straße'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-street",
        )
        zip = colander.SchemaNode(
            colander.String(),
            title=_(u'PLZ'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-zip",
        )
        city = colander.SchemaNode(
            colander.String(),
            title=_(u'Stadt'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-city",
        )
        country = colander.SchemaNode(
            colander.String(),
            title=_(u'Land'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-country",
        )
        representation_type = colander.SchemaNode(
            colander.String(),
            title=_(u"Mein(e) Bevollmächtigte(r) ist:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=rep_type_options,
                readonly=readonly
            ),
            missing=0,
            oid="rep-type",
        )
        note_bottom = colander.SchemaNode(
            colander.String(),
            title='',
            widget=deform.widget.TextInputWidget(
                readonly=True,
                readonly_template="forms/textinput_htmlrendered.pt"
            ),
            missing='',
            default=u'''
<div class="help-block">
    <strong>Hinweis:</strong>
    Du darfst als Deine(n) Bevollmächtigten nur ein Mitglied der Genossenschaft,<br>
    Deine(n) Ehemann/Ehefrau, ein Elternteil, ein Kind oder einen Geschwisterteil benennen.<br>
    Jede(r) Bevollmächtigte kann maximal zwei Mitglieder vertreten.
    (siehe § 13 (6), Satz 3 der <a href="http://url.c3s.cc/satzung" target="_blank" class="alert-link">Satzung</a>)<br>
    <br>
    <strong>Nicht vergessen:</strong>
    Dein(e) Bevollmächtigte(r) muss von eine von Dir unterzeichnete Vollmacht mitbringen<br>
    - bitte keine Kopie, kein Fax, kein Scan, kein Bild, sondern das Original.<br>
    Download für eine Vollmacht: <a href="http://url.c3s.cc/vollmacht" target="_blank" class="alert-link">http://url.c3s.cc/vollmacht</a>
</div>
''',
            oid='rep-note'
        )
        note_bottom.missing=note_bottom.default # otherwise empty on redit
        if readonly:
            note_bottom = None

    class TshirtData(colander.MappingSchema):
        """
        colander schema of tshirt form
        """
        tshirt_type = colander.SchemaNode(
            colander.String(),
            title=_(u"Schnitt:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=tshirt_type_options,
                readonly=readonly
            ),
            missing=0,
            oid="tshirt-type",
        )  
        tshirt_size = colander.SchemaNode( 
            colander.String(),
            title=_(u"Size:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=tshirt_size_options,
                readonly=readonly
            ),
            missing=0,
            oid="tshirt-size",
        )

    ### form

    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Ticketing Information
        - Representation Data
        - Tshirt Data
        """
        ticket = TicketData(
            title=_(u"Ticketinformationen"),
            oid="ticket-data"
        )
        representation = RepresentationData(
            title=_(u"Bevollmächtigte(r)"),
            oid="rep-data"
        )
        if readonly and not appstruct['ticket']['ticket_gv'] == 2:
            representation = None;
        tshirt = TshirtData(
            title=_(u"T-Shirt"),
            oid="tshirt-data"
        )
        if readonly and not appstruct['ticket']['ticket_tshirt']:
            tshirt = None

    return TicketForm(validator=validator).bind()


@view_config(route_name='load_user')
def load_user(request):
    '''
    receive link containing token and load user details
    '''
    _token = request.matchdict['token']
    _email = request.matchdict['email']  # XXX use it for sth?
    #print u"the token: {}".format(_token)
    #print u"the email: {}".format(_email)
    data = json.dumps({"token": _token})
    _auth_header = {
        'X-Messaging-Token': request.registry.settings['yes_auth_token']
    }
    res = requests.put(
        request.registry.settings['yes_api_url'],
        data,
        headers=_auth_header,
    )
    #print u"the result: {}".format(res)
    #print u"the result.reason: {}".format(res.reason)
    #print u"dir(res): {}".format(dir(res))
    try:
        appstruct = {
            'firstname': res.json()['firstname'],
            'lastname': res.json()['lastname'],
            'email': res.json()['email'],
            'token': data
        }
        assert(res.json()['email'] == _email)
        request.session['appstruct_preset'] = appstruct
        return HTTPFound(location=request.route_url('party'))
    except:
        return HTTPFound(location='https://yes.c3s.cc')


@view_config(route_name='party', renderer='templates/party.pt')
def party_view(request):
    """
    the view users use to order a ticket
    """
    #_num_tickets = PartyTicket.get_num_tickets()
    #_num_tickets_paid = PartyTicket.get_num_tickets_paid()

    if 'appstruct' not in request.session:
        if 'appstruct_preset' in request.session:
            appstruct = request.session['appstruct_preset']
        # testing
        else:
            
            appstruct = {
                'firstname': 'TestVorname',
                'lastname': 'TestNachname',
                'email': 'alexander.blum@c3s.cc',
                'token': 'ATOKENTEST'
            }
            request.session['appstruct_preset'] = appstruct
        # /testing
    else:
        appstruct = request.session['appstruct']

    schema = ticket_schema(request, appstruct)

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit'))
            #deform.Button('reset', _(u'Zurücksetzen'))
        ],
        #use_ajax=True,
        renderer=zpt_renderer
    )

    #print "DEBUG: {}".format(dir(request.session['appstruct_preset']))
    if 'appstruct_preset' in request.session:
        #print "found appstruct!"
        #print "the appstruct: {}".format(request.session['appstruct_preset'])
        appstruct = {}
        appstruct['ticket'] = {
            'token': request.session[
                'appstruct_preset']['token'],
            'firstname': request.session[
                'appstruct_preset']['firstname'],
            'lastname': request.session[
                'appstruct_preset']['lastname'],
            'email': request.session[
                'appstruct_preset']['email'],
        }
        form.set_appstruct(appstruct)
        #request.session['appstruct_preset'] = {}  # delete/clear it now
    else:
        return HTTPFound(location='https://yes.c3s.cc')

    # if the form has NOT been used and submitted, remove error messages if any
    if not 'submit' in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        print "submitted!"
        controls = request.POST.items()
        print controls
        try:
            print 'about to validate form input'
            appstruct = form.validate(controls)
            print 'done validating form input'
            print("the appstruct from the form: %s \n") % appstruct
            for thing in appstruct:
                print(u"the thing: %s") % thing
                print(u"type: %s") % type(thing)

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
                'email': appstruct['ticket']['email']
            }

        # make confirmation code
        randomstring = make_random_string()

        # map option to price
        the_values = {
            'ticket_gv_attendance': 0,
            'ticket_bc_attendance': 9,
            'ticket_bc_buffet': 8.5,
            'ticket_tshirt': 25,
            'ticket_all': 40,
        }

        # map option to discount
        the_discounts = {
            'ticket_all': -2.5
        }

        # option 'all' equivalent to all options checked
        if appstruct['ticket']['ticket_gv'] == 1 \
            and set(['attendance', 'buffet']).issubset(
                appstruct['ticket']['ticket_bc']
            ) \
            and appstruct['ticket']['ticket_tshirt']:
            appstruct['ticket']['ticket_all'] = True

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
        if appstruct['ticket']['ticket_all']:
            print("all active")
            _discount = the_discounts.get('ticket_all')
            _the_total = the_values.get('ticket_all')
        else:
            if 'attendance' in appstruct['ticket']['ticket_bc']:
                _the_total += the_values.get('ticket_bc_attendance')
            if 'buffet' in appstruct['ticket']['ticket_bc']:
                _the_total += the_values.get('ticket_bc_buffet')
            if appstruct['ticket']['ticket_tshirt']:
                _the_total += the_values.get('ticket_tshirt')

        appstruct['ticket']['the_total'] = _the_total
        print("_the_total: %s" % _the_total)
        appstruct['ticket']['discount'] = _discount
        print("_discount: %s" % _discount)

        # to store the data in the DB, an object is created
        ticket = PartyTicket(
            token=request.session['appstruct_preset']['token'],
            firstname=request.session['appstruct_preset']['firstname'],
            lastname=request.session['appstruct_preset']['lastname'],
            email=request.session['appstruct_preset']['email'],
            password='',  # appstruct['person']['password'],
            locale=appstruct['ticket']['_LOCALE_'],
            email_is_confirmed=False,
            email_confirm_code=randomstring,
            date_of_submission=datetime.now(),
            num_tickets=1,
            ticket_gv_attendance=appstruct['ticket']['ticket_gv'],
            ticket_bc_attendance=('attendance' in appstruct['ticket']['ticket_bc']),
            ticket_bc_buffet=('buffet' in appstruct['ticket']['ticket_bc']),
            ticket_tshirt=appstruct['ticket']['ticket_tshirt'],
            ticket_tshirt_type=appstruct['tshirt']['tshirt_type'],
            ticket_tshirt_size=appstruct['tshirt']['tshirt_size'],
            ticket_all=appstruct['ticket']['ticket_all'],
            discount=_discount,
            the_total=_the_total,
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
        dbsession = DBSession
        try:
            print "about to add ticket"
            dbsession.add(ticket)
            print "adding ticket"
            appstruct['email_confirm_code'] = randomstring  # XXX
            #                                                 check duplicates
        except InvalidRequestError, e:  # pragma: no cover
            print("InvalidRequestError! %s") % e
        except IntegrityError, ie:  # pragma: no cover
            print("IntegrityError! %s") % ie

        # redirect to success page, then return the PDF
        # first, store appstruct in session
        request.session['appstruct'] = appstruct
        request.session[
            'appstruct']['_LOCALE_'] = appstruct['ticket']['_LOCALE_']
        #
        # empty the messages queue (as validation worked anyways)
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        return HTTPFound(  # redirect to success page
            location=request.route_url('confirm'),
        )

    # if the form was submitted and gathered info shown on the success page,
    # BUT the user wants to correct their information:
    else:
        # remove annoying message from other session
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        if ('appstruct' in request.session):
            #print("form was not submitted, but found appstruct in session.")
            appstruct = request.session['appstruct']
            #print("the appstruct: %s") % appstruct
            # pre-fill the form with the values from last time
            appstruct['ticket'][
                'token'] = request.session['appstruct_preset']['firstname']
            appstruct['ticket'][
                'firstname'] = request.session['appstruct_preset']['firstname']
            appstruct['ticket'][
                'lastname'] = request.session['appstruct_preset']['lastname']
            appstruct['ticket'][
                'email'] = request.session['appstruct_preset']['email'],

            form.set_appstruct(appstruct)

    html = form.render()
    return {
        'form': html,
        'firstname': appstruct['ticket']['firstname'],
        'lastname': appstruct['ticket']['lastname'],
        'email': appstruct['ticket']['email']
    }


@view_config(route_name='confirm',
             renderer='templates/confirm.pt')
def confirm_view(request):
    """
    the form was submitted correctly. show the result.
    """

    if not 'appstruct' in request.session:
        return HTTPFound(location=request.route_url('party'))

    print("DEBUG: request.POST is: %s" % request.POST)

    if 'reedit' in request.POST:  # user wants to re-edit her data
        #print("the form was submitted, the data needs reediting")
        return HTTPFound(location=request.route_url('party'))

    if 'sendmail' in request.POST:  # user wants email w/ transfer info
        #print("the form was submitted, the data confirmed, "
        #      "redirecting to sendmail-view")
        return HTTPFound(location=request.route_url('sendmail'))

    schema = ticket_schema(request, request.session['appstruct'], readonly=True)

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('sendmail',
                          _(u'Ja, schick mir eine Email!')),
            deform.Button('reedit',
                          _(u'Warte, ich will nochmal ändern...'))
        ],
        #use_ajax=True,
        renderer=zpt_renderer
    )

    return {
        'readonlyform': form.render(
            appstruct=request.session['appstruct'])}


@view_config(route_name='sendmail',
             renderer='templates/sendmail.pt')
def sendmail_view(request):
    """
    this view sends a mail to the user and tells her to transfer money
    """
    if 'appstruct' in request.session:
        appstruct = request.session['appstruct']
    else:
        return HTTPFound(location=request.route_url('party'))

    ### email bodies

    #######################################################################
    usermail_with_transaction = \
u'''Hello %s %s !

we have received your ticket order. Please transfer the amount of

            %s Euros

to our bank account:

Bank:             EthikBank eG
Account holder:   C3S SCE
Amount:           € %s
Purpose of use:   Assembly and Barcamp2014 %s
BIC:              GENO DE F1 ETK
IBAN:             DE79 8309 4495 0003 2643 78

As soon as we have received your payment we are going to send you an email 
with your ticket(s) and your other vouchers (catering, t-shirt). Your order 
has to be fully paid by 18th August 2014 latest. The date of entry of 
payment on our account applies.

    See you soon!

    Your C3S Team
''' % (
    appstruct['ticket']['firstname'],
    appstruct['ticket']['lastname'],
    appstruct['ticket']['the_total'],
    appstruct['ticket']['the_total'],
    appstruct['email_confirm_code']
)
    
    #######################################################################
    usermail_without_transaction = \
u'''Hallo %s %s !

Wir haben Deine Ticketbestellung erhalten. 

   Bis bald!
 
   Dein C3S-Team
''' % (
    appstruct['ticket']['firstname'],
    appstruct['ticket']['lastname']
)

    #######################################################################
    usermail_cancelled = \
u'''Hallo %s %s !

?

   Bis bald!
 
   Dein C3S-Team
''' % (
    appstruct['ticket']['firstname'],
    appstruct['ticket']['lastname']
)
    
    #######################################################################
    accmail_body = \
u'''MEMBER:
  name: %s %s
  email: %s
  code: %s
  ga attendance: %s
  bc attendance: %s
  bc buffet: %s
  discount: %s
  total: %s
  comment: %s

REPRESENTATION: %s
  name: %s %s
  street: %s
  zip: %s
  city: %s
  country: %s
  type: %s

TSHIRT: %s
  tshirt type: %s
  tshirt size: %s
''' % (
    appstruct['ticket']['firstname'],
    appstruct['ticket']['lastname'],
    appstruct['ticket']['email'],
    appstruct['email_confirm_code'],
    (appstruct['ticket']['ticket_gv']==1),
    ('attendance' in appstruct['ticket']['ticket_bc']),
    ('buffet' in appstruct['ticket']['ticket_bc']),
    appstruct['ticket']['discount'],
    appstruct['ticket']['the_total'],
    appstruct['ticket']['comment'],
    (appstruct['ticket']['ticket_gv']==2),
    appstruct['representation']['firstname'],
    appstruct['representation']['lastname'],
    appstruct['representation']['street'],
    appstruct['representation']['zip'],
    appstruct['representation']['city'],
    appstruct['representation']['country'],
    appstruct['representation']['representation_type'],
    appstruct['ticket']['ticket_tshirt'],
    appstruct['tshirt']['tshirt_type'],
    appstruct['tshirt']['tshirt_size'],
)

    ### send mails
    mailer = get_mailer(request)

    ### send usermail
    usermail_body = usermail_with_transaction
    if (appstruct['ticket']['the_total'] == 0):
        usermail_body = usermail_without_transaction
    if (appstruct['ticket']['ticket_gv'] == 3):
        usermail_body = usermail_cancelled
    usermail_obj = Message(
        subject=_(u"C3S Party-Ticket: bitte überweisen!"),
        sender="noreply@c3s.cc",
        recipients=[appstruct['ticket']['email']],
        body=usermail_body
    )
    #mailer.send(usermail_obj) #2DO: mails scharf stellen
    print(usermail_body.encode('utf-8'))
    
    ### send accmail
    from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
    accmail_obj = Message(
        subject=_('[C3S_PT] neues ticket'),
        sender="noreply@c3s.cc",
        recipients=[request.registry.settings['c3spartyticketing.mail_rec']],
        #body=encrypt_with_gnupg('''code: %s
        body=accmail_body
    )
    #mailer.send(accmail_obj) #2DO: mails scharf stellen
    print(accmail_body.encode('utf-8'))

    # make the session go away
    request.session.invalidate()
    return {
        'firstname': appstruct['ticket']['firstname'],
        'lastname': appstruct['ticket']['lastname'],
        'transaction': (appstruct['ticket']['the_total'] > 0),
        'canceled': (appstruct['ticket']['ticket_gv'] == 3)
    }


@view_config(route_name='get_ticket')
def get_ticket(request):
    """
    this view gives a user access to her ticket via URL with code
    the response is a PDF download
    """
    _code = request.matchdict['code']
    _email = request.matchdict['email']
    _ticket = PartyTicket.get_by_code(_code)
    if isinstance(_ticket, NoneType):
        return HTTPFound(location=request.route_url('party'))
    if not (_ticket.email == _email):
        #print("no match!")
        return HTTPFound(location=request.route_url('party'))

    # prepare ticket URL with email & code
    # 'https://events.c3s.cc/ci/p1402/' + _ticket.email + _ticket.email_confirm_code
    # 'https://192.168.2.128:6544/ci/p1402/' + _ticket.email + _ticket.email_confirm_code
    _url = request.registry.settings[
        'c3spartyticketing.url'] + '/ci/p1402/' + _ticket.email_confirm_code

    # return a pdf file
    pdf_file = make_qr_code_pdf(_ticket, _url)
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")
    return response


@view_config(route_name='get_ticket_mobile')
def get_ticket_mobile(request):
    """
    this view gives a user access to her ticket via URL with code
    the response is a PDF download
    """
    _code = request.matchdict['code']
    _email = request.matchdict['email']
    _ticket = PartyTicket.get_by_code(_code)
    if isinstance(_ticket, NoneType):
        return HTTPFound(location=request.route_url('party'))
    if not (_ticket.email == _email):
        #print("no match!")
        return HTTPFound(location=request.route_url('party'))

    _url = request.registry.settings[
        'c3spartyticketing.url'] + '/ci/p1402/' + _ticket.email_confirm_code

    # return a pdf file
    pdf_file = make_qr_code_pdf_mobile(_ticket, _url)
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")
    return response


# @view_config(renderer='templates/verify_password.pt',
#              route_name='verify_email_password')
# def success_verify_email(request):
#     """
#     This view is called via links sent in mails to verify mail addresses.
#     It extracts both email and verification code from the URL.
#     It will ask for a password
#     and checks if there is a match in the database.

#     If the password matches, and all is correct,
#     the view shows a download link and further info.
#     """
#     user_email = request.matchdict['email']
#     confirm_code = request.matchdict['code']
#     # if we want to ask the user for her password (through a form)
#     # we need to have a url to send the form to
#     post_url = '/verify/' + user_email + '/' + confirm_code

#     if 'submit' in request.POST:
#         #print("the form was submitted")
#         request.session.pop_flash('message_above_form')
#         request.session.pop_flash('message_above_login')
#         # check for password ! ! !
#         if 'password' in request.POST:
#             _passwd = request.POST['password']
#             #print("The password: %s" % _passwd)
#         #else:
#             # message: missing password!
#         #    print('# message: missing password!')

#         # get matching dataset from DB
#         ticket = PartyTicket.get_by_code(
#             confirm_code)  # returns ticket or None

#         if isinstance(ticket, NoneType):
#             # member not found: FAIL!
#             # print("a matching entry for this code was not found.")
#             not_found_msg = _(
#                 u"Not found. Check verification URL. "
#                 "If all seems right, please use the form again.")
#             return {
#                 'correct': False,
#                 'namepart': '',
#                 'result_msg': not_found_msg,
#             }

#         # check if the password is valid
#         try:
#             correct = PartyTicket.check_password(ticket.id, _passwd)
#         except AttributeError:
#             correct = False
#             request.session.flash(
#                 _(u'Wrong Password!'),
#                 'message_above_login')
#         #print("ticket: %s" % ticket)
#         #print("passwd correct? %s" % correct)
#         # check if info from DB makes sense
#         # -ticket

#         if ((ticket.email == user_email) and correct):
#             #print("-- found ticket, code matches, password too. COOL!")
#             # set the email_is_confirmed flag in the DB for this signee
#             ticket.email_is_confirmed = True
#             #dbsession.flush()
#             namepart = ticket.firstname + ticket.lastname
#             import re
#             PdfFileNamePart = re.sub(  # replace characters
#                 '[^a-zA-Z0-9]',  # other than these
#                 '_',  # with an underscore
#                 namepart)

#             appstruct = {
#                 'firstname': ticket.firstname,
#                 'lastname': ticket.lastname,
#                 'email': ticket.email,
#                 'email_confirm_code': ticket.email_confirm_code,
#                 '_LOCALE_': ticket.locale,
#                 'date_of_submission': ticket.date_of_submission,
#                 'ticket_type': ticket.ticket_type,
#                 'num_tickets': ticket.num_tickets,
#             }
#             request.session['appstruct'] = appstruct

#             # log this person in, using the session
#             #log.info('verified code and password for id %s' % ticket.id)
#             request.session.save()
#             return {
#                 'firstname': ticket.firstname,
#                 'lastname': ticket.lastname,
#                 'code': ticket.email_confirm_code,
#                 'correct': True,
#                 'namepart': PdfFileNamePart,
#                 'result_msg': _("Success. Load your PDF!")
#             }
#     # else: code did not match OR SOMETHING...
#     # just display the form
#     request.session.flash(
#         _(u"Please enter your password."),
#         'message_above_login',
#         allow_duplicate=False
#     )
#     return {
#         'post_url': post_url,
#         'firstname': '',
#         'lastname': '',
#         'namepart': '',
#         'correct': False,
#         'result_msg': "something went wrong."
#     }
