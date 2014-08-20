# -*- coding: utf-8 -*-

import colander
import deform
from deform import ValidationFailure


from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from c3spartyticketing.models import (
    DBSession,
    PartyTicket
)
from c3spartyticketing.views import (
    _,
    zpt_renderer
)
from c3spartyticketing.utils import make_random_string

from datetime import (
    date,
    datetime,
)
from colander import (
    Invalid,
    Range,
)

LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/add_ticket.pt',
             permission='manage',
             route_name='add_ticket')
def add_ticket(request):
    """
    This view lets accountants add a new ticket
    """

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
        if value['personal']['membership_type'] in ('normal', 'investing') \
            and value['ticket']['ticket_gv'] == 2:
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
        if value['represents']['represents1'] != 0:
            if PartyTicket.get_by_id(value['represents']['represents1']) is None:
                raise colander.Invalid(form,
                    'Repräsentiert (1): Ticket ID '
                    +str(value['represents']['represents1'])+' ungültig'
                )
        if value['represents']['represents2'] != 0:
            if PartyTicket.get_by_id(value['represents']['represents2']) is None:
                raise colander.Invalid(form,
                    'Repräsentiert (2): Ticket ID '
                    +str(value['represents']['represents2'])+' ungültig'
                )
        if value['guest']['bc'] != '' and not value['ticket']['ticket_bc']:
            raise colander.Invalid(form,
                'Gästelistenkategorie bei Barcamp angewählt, aber keine Teilnahme'
            )
        if value['guest']['gv'] != '' and not value['ticket']['ticket_gv'] == 1:
            raise colander.Invalid(form,
                'Gästelistenkategorie bei Generalversammlung angewählt, '
                +'aber keine Teilnahme'
            )

    # XXX: convert ticket_*_schema into class an import here
    # from c3spartyticketing.options import (
    #     ticket_gv_options,
    #     ticket_bc_options,
    #     ticket_support_options,
    #     rep_type_options,
    #     tshirt_type_options,
    #     tshirt_size_options,
    # )
    ticket_gv_options = (
        (1, _(u'I will attend the C3S SCE General Assembly.')),
        (2, _(
            u'I will not attend the C3S SCE General Assembly personally. '
            u'I will be represented by an authorized person.'
        )),
        (3, _(u'I will not attend the C3S SCE General Assembly.'))
    )

    ticket_bc_options = (
        ('attendance', _(u'I will attend the BarCamp.')),
        ('buffet', _(u'I\'d like to dine from the BarCamp buffet. (€12)'))
    )

    ticket_support_options = (
        (1, _(u'Supporter Ticket (€5)')),
        (2, _(u'Supporter Ticket XL (€10)')),
        (3, _(u'Supporter Ticket XXL (€100)'))
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

    guest_options_bc = (
        ('', ''),
        ('helper', 'Helfer'),
        ('guest', 'Gast'),
        ('specialguest', 'Ehrengast'),
        ('press', 'Presse'),
    )

    guest_options_gv = (
        ('', ''),
        ('helper', 'Helfer'),
        ('guest', 'Gast'),
        ('specialguest', 'Ehrengast'),
        ('press', 'Presse'),
        ('representative', 'Repräsentant'),
    )

    membership_type_options = (
        ('nonmember', 'Nicht-Mitglied'),
        ('normal', 'Normal'),
        ('investing', 'Investierend'),
    )

    locale_options = (
        ('de', 'deutsch'),
        ('en', 'englisch'),
    )

    ### generate form
    class PersonalData(colander.MappingSchema):

        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"First Name"),
            widget=deform.widget.TextInputWidget(),
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"Last Name"),
            widget=deform.widget.TextInputWidget(),
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u"E-mail"),
            widget=deform.widget.TextInputWidget(),
            validator=colander.Email(),
            oid="email",
        )
        membership_type = colander.SchemaNode(
            colander.String(),
            title="Mitgliedstyp",
            widget=deform.widget.SelectWidget(values=membership_type_options),
            oid="membership-type",
        )
        locale = colander.SchemaNode(
            colander.String(),
            title="Sprache",
            widget=deform.widget.SelectWidget(values=locale_options),
            oid="locale",
        )


    class GuestData(colander.MappingSchema):

        bc = colander.SchemaNode(
            colander.String(),
            title=_(u"BarCamp"),
            widget=deform.widget.SelectWidget(values=guest_options_bc),
            missing='',
            oid="guest-bc",
        )
        gv = colander.SchemaNode(
            colander.String(),
            title=_(u"General Assembly"),
            widget=deform.widget.SelectWidget(values=guest_options_gv),
            missing='',
            oid="guest-gv",
        )

    class TicketData(colander.MappingSchema):

        ticket_gv = colander.SchemaNode(
            colander.Integer(),
            title=_(u"General Assembly:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_gv_options,
            ),
            missing=3,
            oid="ticket_gv"
        )
        ticket_bc = colander.SchemaNode(
            colander.Set(),
            title=_(u"BarCamp:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_bc_options,
            ),
            missing='',
            description='',
            oid="ticket_bc"
        )
        ticket_tshirt = colander.SchemaNode(
            colander.Boolean(),
            title=_(u"Extras:"),
            widget=deform.widget.CheckboxWidget(
            ),
            label="T-shirt (€25)",
            missing='',
            description='',
            oid="ticket_tshirt"
        )
        ticket_all = colander.SchemaNode(
            colander.Boolean(),
            title=_(u"Special Offer:"),
            widget=deform.widget.CheckboxWidget(
            ),
            label="All-Inclusive (€42)",
            missing='',
            description='',
            oid="ticket_all"
        )
        ticket_support = colander.SchemaNode(
            colander.Set(),
            title=_(u"Supporter Tickets:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_support_options,
            ),
            missing='',
            description='',
            oid="ticket_support"
        )

    class RepresentationData(colander.MappingSchema):
        """
        colander schema of respresentation form
        """
        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"First Name"),
            widget=deform.widget.TextInputWidget(
            ),
            missing='',
            oid="rep-firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"Last Name"),
            widget=deform.widget.TextInputWidget(
            ),
            missing='',
            oid="rep-lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u"E-mail"),
            widget=deform.widget.TextInputWidget(
            ),
            missing='',
            oid="rep-email",
        )
        street = colander.SchemaNode(
            colander.String(),
            title=_(u'Address'),
            widget=deform.widget.TextInputWidget(
            ),
            missing='',
            oid="rep-street",
        )
        zip = colander.SchemaNode(
            colander.String(),
            title=_(u'Postal Code'),
            widget=deform.widget.TextInputWidget(
            ),
            missing='',
            oid="rep-zip",
        )
        city = colander.SchemaNode(
            colander.String(),
            title=_(u'City'),
            widget=deform.widget.TextInputWidget(
            ),
            missing='',
            oid="rep-city",
        )
        country = colander.SchemaNode(
            colander.String(),
            title=_(u'Country'),
            widget=deform.widget.TextInputWidget(
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
            ),
            missing=0,
            oid="rep-type",
        )

    class RepresentsData(colander.MappingSchema):
        """
        colander schema of represents
        """
        represents1 = colander.SchemaNode(
            colander.Int(),
            title=_(u"Ticket ID of represented person (1) ..."),
            missing=0,
            oid="represents1",
        )
        represents2 = colander.SchemaNode(
            colander.Int(),
            title=_(u"Ticket ID of represented person (2) ..."),
            missing=0,
            oid="represents2",
        )

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
            ),
            missing=0,
            oid="tshirt-size",
        )

    class PriceData(colander.MappingSchema):
        """
        colander schema of price data
        """
        payment_received = colander.SchemaNode(
            colander.Boolean(),
            title="Zahlungseingang:",
            widget=deform.widget.CheckboxWidget(),
            description='',
            oid="price-payment-received"
        )
        the_total = colander.SchemaNode(
            colander.Decimal(quant='1.00'),
            title="zu zahlen",
            widget=deform.widget.TextInputWidget(
            ),
            default=0,
            oid="price-the-total"
        )
        price_calc = colander.SchemaNode(
            colander.Boolean(),
            title="automatische Berechnung anhand der Ticketinformationen",
            widget=deform.widget.CheckboxWidget(),
            description='',
            oid="price-calc"
        )

    ### form
    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Ticketing Information
        - Representation Data
        - Tshirt Data
        """
        personal = PersonalData(
            title=_(u"Personal Data"),
            oid="personal-data",
        )
        guest = GuestData(
            title="Gästeliste",
            oid="guest-data",
        )
        ticket = TicketData(
            title=_(u"Ticket Information"),
            oid="ticket-data",
        )
        representation = RepresentationData(
            title="Wird repräsentiert von ...",
            oid="rep-data",
        )
        represents = RepresentsData(
            title="Repräsentiert ...",
            oid="represents",
        )
        tshirt = TshirtData(
            title=_(u"T-Shirt"),
            oid="tshirt-data"
        )
        price = PriceData(
            title="Preis",
            oid="order-data"
        )
        staff_comment = colander.SchemaNode(
            colander.String(),
            title=_(u"Staff Kommentar"),
            missing='',
            widget=deform.widget.TextAreaWidget(
                rows=3, cols=50,
            ),
            oid="staff-comment",
        )

    schema = TicketForm(validator=validator)
    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit'))
        ],
        renderer=zpt_renderer
    )
    if 'appstruct' in request.session:
        form.set_appstruct(request.session['appstruct'])

    # if the form has NOT been used and submitted, remove error messages if any
    if not 'submit' in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        print("submitted!")
        controls = request.POST.items()
        print(controls)

        ### validation of user input

        try:
            print('about to validate form input')
            appstruct = form.validate(controls)
            print('done validating form input')
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

        ### derived values

        # member
        if appstruct['personal']['membership_type'] in ('normal', 'investing'):

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

            # guest auto calc
            if appstruct['guest']['gv'] == 'helper':
                the_values['ticket_tshirt'] = 0
            if appstruct['guest']['gv'] == 'guest':
                pass
            if appstruct['guest']['gv'] == 'specialguest':
                pass
            if appstruct['guest']['gv'] == 'press':
                pass
            if appstruct['guest']['bc'] == 'helper':
                the_values['ticket_bc_attendance'] = 0
                the_values['ticket_bc_buffet'] = 0
                the_values['ticket_tshirt'] = 0
            if appstruct['guest']['bc'] == 'guest':
                pass
            if appstruct['guest']['bc'] == 'specialguest':
                the_values['ticket_bc_attendance'] = 0
                the_values['ticket_bc_buffet'] = 0
            if appstruct['guest']['bc'] == 'press':
                the_values['ticket_bc_attendance'] = 0
                the_values['ticket_bc_buffet'] = 0

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

            derivedvalues= {}
            derivedvalues['the_total'] = _the_total
            derivedvalues['discount'] = _discount
            derivedvalues['support'] = _support    

        # nonmember
        else:
            # remove member values
            appstruct['ticket']['ticket_gv'] = 3
            appstruct['representation']['firstname'] = ''
            appstruct['representation']['lastname'] = ''
            appstruct['representation']['street'] = ''
            appstruct['representation']['zip'] = ''
            appstruct['representation']['city'] = ''
            appstruct['representation']['country'] = ''
            appstruct['representation']['representation_type'] = 0

            # map option to price
            the_values = {
                'ticket_bc_attendance': 11,
                'ticket_bc_buffet': 12,
                'ticket_tshirt': 25,
                'ticket_all': 42,
            }

            # map supporter tickets to price
            the_support = {
                1: 5,
                2: 10,
                3: 100
            }

            # guest auto calc
            if appstruct['guest']['bc'] == 'helper':
                the_values['ticket_bc_attendance'] = 0
                the_values['ticket_bc_buffet'] = 0
                the_values['ticket_tshirt'] = 0
            if appstruct['guest']['bc'] == 'guest':
                pass
            if appstruct['guest']['bc'] == 'specialguest':
                the_values['ticket_bc_attendance'] = 0
                the_values['ticket_bc_buffet'] = 0
            if appstruct['guest']['bc'] == 'press':
                the_values['ticket_bc_attendance'] = 0
                the_values['ticket_bc_buffet'] = 0

            # bc: buffet only when attended
            if 'attendance' not in appstruct['ticket']['ticket_bc']:
                appstruct['ticket']['ticket_bc'].discard('buffet')

            # calculate the total sum and discount
            _the_total = 0
            _support = 0
            if 'attendance' in appstruct['ticket']['ticket_bc']:
                _the_total += the_values.get('ticket_bc_attendance')
            if 'buffet' in appstruct['ticket']['ticket_bc']:
                _the_total += the_values.get('ticket_bc_buffet')
            if appstruct['ticket']['ticket_tshirt']:
                _the_total += the_values.get('ticket_tshirt')
            for support in appstruct['ticket']['ticket_support']:
                _the_total += the_support.get(int(support))
                _support += the_support.get(int(support))

            derivedvalues= {}
            derivedvalues['the_total'] = _the_total
            derivedvalues['discount'] = 0
            derivedvalues['support'] = _support

        # auto calc or manual entry
        if appstruct['price']['price_calc']:
            appstruct['price']['the_total'] = derivedvalues['the_total']
            appstruct['price']['price_calc'] = False
        else:
            derivedvalues['discount'] = 0
            derivedvalues['the_total'] = appstruct['price']['the_total']

        ### create in db
        randomstring = make_random_string()
        _ticket = PartyTicket(
            token=None,
            firstname=appstruct['personal']['firstname'],
            lastname=appstruct['personal']['lastname'],
            email=appstruct['personal']['email'],
            password='',  # appstruct['person']['password'],
            locale=appstruct['personal']['locale'],
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
            support=derivedvalues['support'],
            discount=derivedvalues['discount'],
            the_total=derivedvalues['the_total'],
            rep_firstname=appstruct['representation']['firstname'],
            rep_lastname=appstruct['representation']['lastname'],
            rep_street=appstruct['representation']['street'],
            rep_zip=appstruct['representation']['zip'],
            rep_city=appstruct['representation']['city'],
            rep_country=appstruct['representation']['country'],
            rep_type=appstruct['representation']['representation_type'],
            guestlist=False,
            user_comment='',
        )
        _ticket.rep_email = appstruct['representation']['email']
        _ticket.membership_type = appstruct['personal']['membership_type']

        _ticket.guestlist_bc = appstruct['guest']['bc']
        _ticket.guestlist_gv = appstruct['guest']['gv']

        _ticket.represents_id1 = appstruct['represents']['represents1']
        _ticket.represents_id2 = appstruct['represents']['represents2']

        # zahlungseingang / datum
        _ticket.payment_received = appstruct['price']['payment_received']
        if _ticket.payment_received is True:
            _ticket.payment_received_date = datetime.now()
        else:
            _ticket.payment_received_date = datetime(
                1970, 1, 1)

        # staff comment
        if appstruct['staff_comment']:
            _ticket.staff_comment
            _ticket.staff_comment = (_ticket.staff_comment or u'') \
                + '\r\n\r\n' \
                + '-'*80 \
                + '\r\n' \
                + str(datetime.now()) + ' | ' + str(request.user.login) + ':' \
                + '\r\n\r\n' \
                + unicode(appstruct['staff_comment'])
            appstruct['staff_comment'] = ''

        DBSession.add(_ticket)
        DBSession.flush()  # save to DB
        print('backend - save to db: created.')
        
        return HTTPFound(
            location=request.route_url(
                'edit_ticket',
                ticket_id=_ticket.id
            )
        )

    _html = form.render()
    return {
        'form': _html
    }
