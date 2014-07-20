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

from pyramid.renderers import render

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
        # XXX: herausfinden, wie man per klassenvalidator colander.Invalid
        #      ansprechen muss, damit deform den error am richtigen ort
        #      platziert und die richtigen klassen vergibt
        # node.raise_invalid()?
        # add exc as child?
        #form.raise_invalid('test', form.get('tshirt').get('tshirt_size'))
        if value['ticket']['ticket_tshirt']:
            if not value['tshirt']['tshirt_type']:
                raise colander.Invalid(form,
                    _(u'Gender selection for T-shirt is mandatory.')
                )
            if not value['tshirt']['tshirt_size']:
                raise colander.Invalid(form,
                    _(u'Size of T-shirt ist mandatory.')
                )
        if value['ticket']['ticket_gv'] == 2:
            if not value['representation']['firstname']:
                raise colander.Invalid(form,
                    _(u'First name of representative is mandatory.')
                )
            if not value['representation']['lastname']:
                raise colander.Invalid(form,
                    _(u'Last name of representative is mandatory.')
                )
            validate_email = colander.Email(
                _(u'Email of representative is invalid.')
            )
            validate_email(
                form.get('representation').get('email'),
                value['representation']['email']
            )
            if not value['representation']['street']:
                raise colander.Invalid(form,
                    _(u'Address of representative is mandatory.')
                )
            if not value['representation']['zip']:
                raise colander.Invalid(form,
                    _(u'Postal code of representative is mandatory.')
                )
            if not value['representation']['city']:
                raise colander.Invalid(form,
                    _(u'City of representative is mandatory.')
                )
            if not value['representation']['country']:
                raise colander.Invalid(form,
                    _(u'Country of representative is mandatory.')
                )
            if not value['representation']['representation_type']:
                raise colander.Invalid(form,
                    _(u'Relation of representative is mandatory.')
                )

    ### options

    ticket_gv_options = (
        (1, _(u'I will attend the C3S SCE General Assembly.')),
        (2, _(
            u'I will not attend the C3S SCE General Assembly personally. '
            u'I will be represented by an authorized person.'
        )),
        (3, _(u'I will not attend the C3S SCE General Assembly.'))
    )

    ticket_bc_options = (
        ('attendance', _(u'I will attend the BarCamp. (€9)')),
        ('buffet', _(u'I\'d like to dine from the BarCamp buffet. (€12)'))
    )

    ticket_support_options = (
        (1, _(u'Supporter Ticket (€5)')),
        (2, _(u'Supporter Ticket X (€10)')),
        (3, _(u'Supporter Ticket XL (€100)'))
    )

    rep_type_options = (
        ('member', _(u'a member of C3S SCE')),
        ('partner', _(u'my spouse / registered civil partner')),
        ('parent', _(u'my parent')),
        ('child', _(u'my child')),
        ('sibling', _(u'my sibling'))
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
            title=_(u"General Assembly:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_gv_options,
                readonly=readonly
            ),
            oid="ticket_gv"
        )
        ticket_bc = colander.SchemaNode(
            colander.Set(),
            title=_(u"BarCamp:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_bc_options,
                readonly=readonly
            ),
            missing='',
            description=_(
                u'The buffet consists of e.g., salads, vegetables, dips, '
                u'cheese and meat platters. A free drink is included.'
            ),
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
            label="T-shirt (€25)",
            missing='',
            description=_(
                u'There will be one joint T-shirt design for both events in '
                u'C3S green, black and white. Exclusively for participants, '
                u'available only if pre-ordered! You can collect your '
                u'pre-ordered T-shirt at both the BarCamp and the general '
                u'assembly. If you chose to order a shirt, '
                u'you can specify its size below.'
            ),
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
            label="All-Inclusive (€42)",
            missing='',
            description=_(
                u'The all-inclusive package covers the participation in the '
                u'BarCamp (including buffet and free drink), participation '
                u'in the general assembly, and the exclusive event T-shirt as '
                u'well.'
            ),
            oid="ticket_all"
        )
        if readonly:
            ticket_all.description = None
            ticket_all.label = _(u"All-Inclusive Discount (-€2,50)")
            if not appstruct['ticket']['ticket_all']:
                ticket_all = None
        ticket_support  = colander.SchemaNode(
            colander.Set(),
            title=_(u"Supporter Tickets:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_support_options,
                readonly=readonly
            ),
            missing='',
            description=_(
                u'These ticket options are selectable indepently from the '
                u'other options. They help the cooperative a great deal to '
                u'bear the costs occasioned by the events.'
            ),
            oid="ticket_support"
        )
        if readonly:
            ticket_support.description = None
            if not appstruct['ticket']['ticket_support']:
                ticket_support = None
        if readonly and appstruct['ticket']['the_total'] > 0:
            the_total = colander.SchemaNode(
                colander.Decimal(quant='1.00'),
                widget=deform.widget.TextInputWidget(
                    readonly=readonly,
                    readonly_template="forms/textinput_money.pt",
                ),
                title=_(u"Total"),
                description=_(
                    u'Your order has to be fully paid by 18.08.2014 at the '
                    u'latest (payment receipt on our account applies)'
                    u'Otherwise we will have to cancel the entire order. Money '
                    u'transfer is the only payment method. Payment '
                    u'informations will be sent to you shortly by e-mail.'
                ),
                oid="the-total",
            )
        comment = colander.SchemaNode(
            colander.String(),
            title=_(u"Notes"),
            missing='',
            validator=colander.Length(max=250),
            widget=deform.widget.TextAreaWidget(
                rows=3, cols=50,
                readonly=readonly
            ),
            description=_(u"Your notes (255 chars)"),
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
            default=request.session['userdata']['token'],
            missing='',
            oid="firstname",
        )
        firstname = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['userdata']['firstname'],
            missing='',
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['userdata']['lastname'],
            missing='',
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=request.session['userdata']['email'],
            missing='',
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
            <p>
               Please provide us with the following information for your
               representative:
            <p>''',
            missing='',
            oid='rep-note'
        )
        if get_locale_name(request) == 'de':
            note_top = colander.SchemaNode(
                colander.String(),
                title='',
                widget=deform.widget.TextInputWidget(
                    readonly=True,
                    readonly_template="forms/textinput_htmlrendered.pt"
                ),
                default=u'''
            <p>
                Wir brauchen von Dir folgende Daten de(s/r) Bevollmächtigten:
            <p>''',
                missing='',
                oid='rep-note'
            )
        #note_top.default = None
        note_top.missing=note_top.default # otherwise empty on redit
        if readonly:
            note_top = None
        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"First Name"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"Last Name"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u"E-mail"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-email",
        )
        street = colander.SchemaNode(
            colander.String(),
            title=_(u'Address'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-street",
        )
        zip = colander.SchemaNode(
            colander.String(),
            title=_(u'Postal Code'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-zip",
        )
        city = colander.SchemaNode(
            colander.String(),
            title=_(u'City'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-city",
        )
        country = colander.SchemaNode(
            colander.String(),
            title=_(u'Country'),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            missing='',
            oid="rep-country",
        )
        representation_type = colander.SchemaNode(
            colander.String(),
            title=_(u"My representative is..."),
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
                <strong>Please note:</strong>
                You may only nominate as your representative members
                of the cooperative, your spouse, parents, children or
                siblings. Each representative may represent two members
                at most (see § 13 (6), sentence 3, of the articles of
                <a href='http://url.c3s.cc/statutes' target='_blank'>
                    association
                </a>).
                Registered civil partners are treated as spouses.
                <br>
                <strong>Don't forget:</strong>
                Your representative has to provide an authorization
                certificate signed by you. Please do not bring or send
                a copy, fax, scan, or picture. We can only accept the
                original document.
                <br>
                Download authorization form:
                <a href='http://url.c3s.cc/authorization' target='_blank'>
                    http://url.c3s.cc/authorization
                </a>
            </div>''',
            oid='rep-note'
        )
        if get_locale_name(request) == 'de':
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
                Du darfst als Deine(n) Bevollmächtigten nur ein
                Mitglied der Genossenschaft, Deine(n) Ehemann/Ehefrau,
                ein Elternteil, ein Kind oder einen Geschwisterteil
                benennen. Jede(r) Bevollmächtigte kann maximal zwei
                Mitglieder vertreten (siehe § 13 (6), Satz 3 der
                <a href='http://url.c3s.cc/satzung' target='_blank'>
                    Satzung
                </a>).
                Eingetragene Lebenspartner werden wie Ehegatten behandelt.
                <br>
                <strong>Nicht vergessen:</strong>
                Dein(e) Bevollmächtigte(r) muss von eine von Dir
                unterzeichnete Vollmacht mitbringen - bitte keine
                Kopie, kein Fax, kein Scan, kein Bild, sondern das
                Original.
                <br>
                Download für den Vordruck einer Vollmacht:
                <a href='http://url.c3s.cc/vollmacht' target='_blank'>
                    http://url.c3s.cc/vollmacht
                </a>
            </div>''',
                oid='rep-note'
            )
        note_bottom.missing=note_bottom.default # otherwise empty on reedit
        if readonly:
            note_bottom = None

    class TshirtData(colander.MappingSchema):
        """
        colander schema of tshirt form
        """
        tshirt_type = colander.SchemaNode(
            colander.String(),
            title=_(u"Gender:"),
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
            title=_(u"Ticket Information"),
            oid="ticket-data",
        )
        representation = RepresentationData(
            title=_(u"Representative"),
            oid="rep-data",
        )
        if readonly and not appstruct['ticket']['ticket_gv'] == 2:
            representation = None;
        tshirt = TshirtData(
            title=_(u"T-Shirt"),
            oid="tshirt-data"
        )
        if readonly and not appstruct['ticket']['ticket_tshirt']:
            tshirt = None
        finalnote = colander.SchemaNode(
            colander.String(),
            title='',
            widget=deform.widget.TextInputWidget(
                readonly=True,
                readonly_template="forms/textinput_htmlrendered.pt"
            ),
            default=u'''
            <div class="alert alert-info" role="alert">
                <strong>
                    We will send tickets and vouchers in time by e-mail
                </strong><br />
                You can't edit the order form after hitting the button
                "Submit & Buy" below. However, you can click the personal
                link you received as part of the invitation link. There you
                can view but not edit your order. A full refund of your
                money once transferred is not possible. Only in case the
                BarCamp is cancelled by C3S SCE a refund for the BarCamp
                ticket and food is possible. If you have any questions
                please contact
                <a href="mailto:office@c3s.cc" class="alert-link">
                    office@c3s.cc
                </a>
            </div>''',
            missing='',
            oid='final-note'
        )
        if get_locale_name(request) == 'de':
            finalnote = colander.SchemaNode(
                colander.String(),
                title='',
                widget=deform.widget.TextInputWidget(
                    readonly=True,
                    readonly_template="forms/textinput_htmlrendered.pt"
                ),
                default=u'''
            <div class="alert alert-info" role="alert">
                <strong>
                    Wir versenden die Tickets und Gutscheine rechtzeitig per
                    Email.
                </strong><br />
                Sobald Du das Bestellformular mit dem Button "Absenden &
                Kaufen" unten absendest, kannst Du an der Bestellung im
                Formular keine Änderung mehr vornehmen. Du kannst Deine
                Bestellung jedoch unter Deinem persönlichen Link aus der
                Einladungs-Mail weiterhin aufrufen und anschauen. Eine
                Erstattung der überwiesenen Summe ist nicht möglich. Nur
                im Fall der Absage des Barcamps durch die C3S SCE werden
                die Kosten für Ticket und Essen erstattet. Falls Du Fragen
                zu Deiner Bestellung hast, wende Dich bitte an
                <a href="mailto:office@c3s.cc" class="alert-link">
                    office@c3s.cc
                </a>
            </div>''',
                missing='',
                oid='final-note'
            )
        finalnote.missing=finalnote.default # otherwise empty on redit
        if not readonly:
            finalnote = None

    return TicketForm(validator=validator).bind()


def ticket_appstruct(request, view=''):
    '''
        Ensures the consistent creation of a valid ticket appstruct.
        Tries creation in the following order:
        1. Use from possibly edited session (reedit, refresh)
        2. If id not given, create new from userdata
        3. If id given, create from dbenty
        4. Redirect to access denied url
    '''
    print('--- creating appstract ------------------------------------------')

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
            'ticket_all': _ticket.ticket_all,
            'ticket_support': [
                '1',
                '2',
                '3'
            ],
            'support': _ticket.support,
            'the_total': _ticket.the_total,
            'comment': _ticket.user_comment,
            'ticket_tshirt': _ticket.ticket_tshirt,
            'firstname': _ticket.firstname,
            'lastname': _ticket.lastname,
            'token': _ticket.token,
            'email': _ticket.email,
            '_LOCALE_': ticket.locale
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
        'tshirt': {
            'tshirt_type': _ticket.ticket_tshirt_type,
            'tshirt_size': _ticket.ticket_tshirt_size
        }
    }
    if not _ticket.ticket_bc_attendance:
        appstruct['ticket']['ticket_bc'].remove('attendance')
    if not _ticket.ticket_bc_buffet:
        appstruct['ticket']['ticket_bc'].remove('buffet')
    if not _ticket.ticket_support:
        appstruct['ticket']['ticket_support'].remove('1')
    if not _ticket.ticket_support_x:
        appstruct['ticket']['ticket_support'].remove('2')
    if not _ticket.ticket_support_xl:
        appstruct['ticket']['ticket_support'].remove('3')

    print "-- appstruct: {}".format(appstruct)
    return appstruct


def check_route(request, view=''):
    '''
        A. checks:
            1.  userdata check:
                userdata has to be set in load_user. load_user() is the only
                entrance door. if userdata is not set,
                redirect to access denied url

            3.  dbentry check:
                if finish_on_submit is active and user has already submitted,
                redirect to finished view

            4.  date check:
                if registration period is over,
                redirect to finished view

        B. individual routes:
            redirects based on keywords in POST
    '''
    print('--- pick route --------------------------------------------------')
    if view:
        print('called from view: %s') % view

    ### checks

    # userdata check:
    if 'userdata' in request.session:
        userdata = request.session['userdata']
        assert('token' in userdata)
        assert('id' in userdata)
        assert('firstname' in userdata)
        assert('lastname' in userdata)
        assert('email' in userdata)
        assert('mtype' in userdata)
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
        registration_end = dateutil.parser.parse(
            request.registry.settings['registration.end']
        ).date()
        if today > registration_end:
            print('date check: registration is finished. redirecting ...')
            return HTTPFound(location=request.route_url('finished'))
        else:
            print('date check: registration is still possible')

    ### individual routes

    # confirm view:
    if view is 'confirm':

        # reedit: user wants to re-edit her data
        if 'reedit' in request.POST:
            return HTTPFound(location=request.route_url('party')+'?reedit')

        # order: user confirmed the data
        if 'confirmed' in request.POST:
            return HTTPFound(location=request.route_url('success'))

        if not 'appstruct' in request.session:
            return HTTPFound(location=request.route_url('party'))

    # success view:
    if view is 'success':

        # confirmed: test flag
        if 'flags' not in request.session \
            or 'confirmed' not in request.session['flags']:
            return HTTPFound(location=request.route_url('party'))

        if not 'appstuct' in request.session:
            return HTTPFound(location=request.route_url('party'))

    return


@view_config(route_name='load_user')
def load_user(request):
    '''
    receive link containing token and load user details. saves details in
    userdata. userdata should only be changed in this view. load_user is the
    only entrance door.
    '''
    print('--- load user ---------------------------------------------------')

    _token = request.matchdict['token']
    _email = request.matchdict['email']

    ### delete any previous appstruct
    if 'userdata' in request.session:
        request.session['userdata'] = None
    # XXX think about a nicer abstract way to save derived values (->form 
    # object) and flags, which control the flow
    if 'derivedvalues' in request.session:
        request.session['derivedvalues'] = None
    if 'flags' in request.session:
        request.session['flags'] = None

    ### load userdata from dbentry
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
                'email_confirm_code': _ticket.email_confirm_code
            }
            request.session['userdata'] = userdata
            return HTTPFound(location=request.route_url('party'))
    except:
        print "no valid dbentry found."
        pass

    ### load userdata from membership app
    data = json.dumps({"token": _token})
    print('querying MGV API ...')
    _auth_header = {
        'X-Messaging-Token': request.registry.settings['yes_auth_token']
    }
    res = requests.put(
        request.registry.settings['yes_api_url'],
        data,
        headers=_auth_header,
    )
    #print u"the result: {}".format(res)
    #print u"the result.json(): {}".format(res.json())
    #print u"the result.reason: {}".format(res.reason)
    #print u"dir(res): {}".format(dir(res))
    try:
        userdata = {
            'token': _token,
            'id': 'None',
            'firstname': res.json()['firstname'],
            'lastname': res.json()['lastname'],
            'email': res.json()['email'],
            'mtype': res.json()['mtype']
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


@view_config(route_name='party', renderer='templates/party.pt')
def party_view(request):
    """
    the view users use to order a ticket
    """

    ### pick route
    route = check_route(request, 'party')
    if isinstance(route, HTTPRedirection):
        return route

    ### generate appstruct
    appstruct = ticket_appstruct(request, 'party')

    ### generate form
    schema = ticket_schema(request, appstruct)
    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit'))
        ],
        #use_ajax=True,
        renderer=zpt_renderer
    )
    form.set_appstruct(appstruct)

    # if the form has NOT been used and submitted, remove error messages if any
    if not 'submit' in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        print "submitted!"
        controls = request.POST.items()
        print controls

        ### validation of user input

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
                'formerror': True
            }

        ### derived values

        # map option to price
        the_values = {
            'ticket_gv_attendance': 0,
            'ticket_bc_attendance': 9,
            'ticket_bc_buffet': 12,
            'ticket_tshirt': 25,
            'ticket_all': 42,
        }

        # map option to discount
        the_discounts = {
            'ticket_all': -2.5
        }

        # map supporter tickets to price
        the_support = {
            1: 5,
            2: 10,
            3: 100
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
        _support = 0
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
            'confirmed': True
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
        'reedit': ('reedit' in request.GET)
    }


@view_config(route_name='confirm',
             renderer='templates/confirm.pt')
def confirm_view(request):
    """
    the form was submitted correctly. show the result for the user to confirm
    """

    ### pick route
    route = check_route(request, 'confirm')
    if isinstance(route, HTTPRedirection):
        return route

    ### generate appstruct
    appstruct = ticket_appstruct(request, 'confirm')

    ### generate form
    schema = ticket_schema(request, request.session['appstruct'], readonly=True)
    button_submit_text = _(u'Submit & Buy')
    if appstruct['ticket']['the_total'] == 0:
        button_submit_text = _(u'Submit')
    form = deform.Form(
        schema,
        buttons=[
            deform.Button('confirmed', button_submit_text),
            deform.Button('reedit', _(u'Wait, I might have to change...'))
        ],
        #use_ajax=True,
        renderer=zpt_renderer
    )

    return {
        'readonlyform': form.render(
            appstruct=request.session['appstruct'])}


@view_config(route_name='success',
             renderer='templates/success.pt')
def sendmail_view(request):
    """
    the user has confirmed the order
        1. save to db (update, if token exists in db; create otherwise)
        2. send emails (usermail, accmail)
        3. show userfeedback
    """

    ### pick route
    route = check_route(request, 'success')
    if isinstance(route, HTTPRedirection):
        return route

    ### generate appstruct
    appstruct = ticket_appstruct(request, 'success')
    
    ### save to db

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
        ticket.ticket_tshirt = appstruct['ticket']['ticket_tshirt']
        ticket.ticket_tshirt_type = appstruct['tshirt']['tshirt_type']
        ticket.ticket_tshirt_size = appstruct['tshirt']['tshirt_size']
        ticket.ticket_all = appstruct['ticket']['ticket_all']
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
            ticket_tshirt=appstruct['ticket']['ticket_tshirt'],
            ticket_tshirt_type=appstruct['tshirt']['tshirt_type'],
            ticket_tshirt_size=appstruct['tshirt']['tshirt_size'],
            ticket_all=appstruct['ticket']['ticket_all'],
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
        #dbsession = DBSession
        try:
            DBSession.add(ticket)
            print('save to db: created.')
            appstruct['email_confirm_code'] = randomstring  # XXX
            #                                    check duplicates
        except InvalidRequestError, e:  # pragma: no cover
            print("InvalidRequestError! %s") % e
        except IntegrityError, ie:  # pragma: no cover
            print("IntegrityError! %s") % ie

    ### render emails

    # sanity check of local_name; XXX put into subscripber.py
    lang = request.registry.settings['pyramid.default_locale_name']
    langs = request.registry.settings['available_languages'].split()
    if request.locale_name in langs:
        lang = request.locale_name

    #######################################################################
    usermail_gv_transaction_subject = _(
        u'C3S General Assembly & Barcamp 2014: your participation & order'
    )
    usermail_gv_transaction = render(
        'templates/mails/usermail_gv_transaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'the_total': appstruct['ticket']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code']
        }
    )

    #######################################################################
    usermail_gv_notransaction_subject = _(
        u'C3S General Assembly & Barcamp 2014: your participation'
    )
    usermail_gv_notransaction = render(
        'templates/mails/usermail_gv_notransaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname']
        }
    )

    #######################################################################
    usermail_notgv_bc_subject = _(
        u'C3S General Assembly & Barcamp 2014: your BarCamp ticket / '
        u'your cancellation of the general assembly'
    )
    usermail_notgv_bc = render(
        'templates/mails/usermail_notgv_bc-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'the_total': appstruct['ticket']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code']
        }
    )

    #######################################################################
    usermail_notgv_notbc_transaction_subject = _(
        u'C3S General Assembly & Barcamp 2014: your cancellation / your order'
    )
    usermail_notgv_notbc_transaction = render(
        'templates/mails/usermail_notgv_notbc_transaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname'],
            'the_total': appstruct['ticket']['the_total'],
            'email_confirm_code': appstruct['email_confirm_code']
        }
    )

    #######################################################################
    usermail_notgv_notbc_notransaction_subject = _(
        u'C3S General Assembly & Barcamp 2014: your cancellation'
    )
    usermail_notgv_notbc_notransaction = render(
        'templates/mails/usermail_notgv_notbc_notransaction-'+lang+'.pt',
        {
            'firstname': appstruct['ticket']['firstname'],
            'lastname': appstruct['ticket']['lastname']
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
            'gv_attendance': (appstruct['ticket']['ticket_gv'] == 1),
            'bc_attendance': (
                'attendance' in appstruct['ticket']['ticket_bc']),
            'bc_buffet': ('buffet' in appstruct['ticket']['ticket_bc']),
            'discount': appstruct['ticket']['discount'],
            'the_total': appstruct['ticket']['the_total'],
            'comment': appstruct['ticket']['comment'],
            'gv_representation': (appstruct['ticket']['ticket_gv'] == 2),
            'rep_firstname': appstruct['representation']['firstname'],
            'rep_lastname': appstruct['representation']['lastname'],
            'rep_email': appstruct['representation']['email'],
            'rep_street': appstruct['representation']['street'],
            'rep_zip': appstruct['representation']['zip'],
            'rep_city': appstruct['representation']['city'],
            'rep_country': appstruct['representation']['country'],
            'rep_type': appstruct['representation']['representation_type'],
            'tshirt': appstruct['ticket']['ticket_tshirt'],
            'tshirt_type': appstruct['tshirt']['tshirt_type'],
            'tshirt_size': appstruct['tshirt']['tshirt_size'],
            'supporter': ('1' in appstruct['ticket']['ticket_support']),
            'supporter_x': ('2' in appstruct['ticket']['ticket_support']),
            'supporter_xl': ('3' in appstruct['ticket']['ticket_support'])
        }
    )

    ### send mails
    mailer = get_mailer(request)

    ### pick usermail
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

    ### pick usermail
    usermail_obj = Message(
        subject=usermail_subject,
        sender=request.registry.settings['c3spartyticketing.mail_sender'],
        recipients=[appstruct['ticket']['email']],
        body=usermail_body
    )

    if 'true' in request.registry.settings['testing.mail_to_console']:
        # ^^ yes, a little ugly, but works; it's a string
        #print "printing mail"
        print(usermail_body.encode('utf-8'))
    else:
        #print "sending mail"
        mailer.send(usermail_obj)

    ### send accmail
    from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
    accmail_obj = Message(
        subject=accmail_subject,
        sender=request.registry.settings['c3spartyticketing.mail_sender'],
        recipients=[request.registry.settings['c3spartyticketing.mail_rec']],
        body=encrypt_with_gnupg(accmail_body)
    )
    if 'true' in request.registry.settings['testing.mail_to_console']:
        print(accmail_body.encode('utf-8'))
    else:
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


@view_config(route_name='finished',
             renderer='templates/finished.pt')
def finished_view(request):
    """
    show the ticket readonly, e.g. if user has already submitted and 
    finish_on_submit is on
    """

    ### pick route
    route = check_route(request, 'finished')
    if isinstance(route, HTTPRedirection):
        return route

    ### generate appstruct
    appstruct = ticket_appstruct(request, 'finished')

    ### generate form
    schema = ticket_schema(request, appstruct, readonly=True)
    form = deform.Form(
        schema,
        buttons=[],
        #use_ajax=True,
        renderer=zpt_renderer
    )

    return {
        'readonlyform': form.render(
            appstruct=appstruct
        ),
        'token': request.session['userdata']['email_confirm_code']
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
