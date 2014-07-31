# -*- coding: utf-8 -*-

import colander
import deform
from deform import ValidationFailure


from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


from c3spartyticketing.models import PartyTicket
from c3spartyticketing.views import (
    _,
    zpt_renderer
)


@view_config(renderer='templates/edit_ticket.pt',
             permission='manage',
             route_name='edit_ticket')
def edit_ticket(request):
    """
    This view lets accountants edit ticket details
    """
    tid = request.matchdict['ticket_id']

    _ticket = PartyTicket.get_by_id(tid)

    if _ticket is None:  # that id did not produce good results
        return HTTPFound(  # back to base
            request.route_url('dashboard',
                              number=0,))

    ### generate appstruct
    appstruct = {
        'ticket': {
            'ticket_gv': _ticket.ticket_gv_attendance,
            'ticket_bc': [
                'attendance' if _ticket.ticket_bc_attendance else None,
                'buffet' if _ticket.ticket_bc_buffet else None,
            ],
            'ticket_all': _ticket.ticket_all,
            'ticket_support': [_ticket.ticket_all],
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
        'tshirt': {
            'tshirt_type': _ticket.ticket_tshirt_type,
            'tshirt_size': _ticket.ticket_tshirt_size
        }
    }

    from c3spartyticketing.options import (
        ticket_gv_options,
        ticket_bc_options,
        ticket_support_options,
        rep_type_options,
        tshirt_type_options,
        tshirt_size_options,
    )

    ### generate form
    class TicketData(colander.MappingSchema):

        locale_name = _ticket.locale
        ticket_gv = colander.SchemaNode(
            colander.Integer(),
            title=_(u"General Assembly:"),
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_gv_options,
            ),
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
            description=_(
                u'The buffet consists of e.g., salads, vegetables, dips, '
                u'cheese and meat platters. A free drink is included.'
            ),
            oid="ticket_bc"
        )
        ticket_tshirt = colander.SchemaNode(
            colander.Boolean(),
            title=_(u"Extras:"),
            widget=deform.widget.CheckboxWidget(
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
        ticket_all = colander.SchemaNode(
            colander.Boolean(),
            title=_(u"Special Offer:"),
            widget=deform.widget.CheckboxWidget(
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
        ticket_support = colander.SchemaNode(
            colander.Set(),
            title=_(u"Supporter Tickets:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_support_options,
            ),
            missing='',
            description=_(
                u'These ticket options are selectable indepently from the '
                u'other options. They help the cooperative a great deal to '
                u'bear the costs occasioned by the events.'
            ),
            oid="ticket_support"
        )
        comment = colander.SchemaNode(
            colander.String(),
            title=_(u"Notes"),
            missing='',
            validator=colander.Length(max=250),
            widget=deform.widget.TextAreaWidget(
                rows=3, cols=50,
            ),
            description=_(u"Your notes (255 chars)"),
            oid="comment",
        )
        # # hidden fields for personal data
        # token = colander.SchemaNode(
        #     colander.String(),
        #     widget=deform.widget.HiddenWidget(),
        #     missing='',
        #     oid="firstname",
        # )
        # firstname = colander.SchemaNode(
        #     colander.String(),
        #     widget=deform.widget.HiddenWidget(),
        #     default=request.session['userdata']['firstname'],
        #     missing='',
        #     oid="firstname",
        # )
        # lastname = colander.SchemaNode(
        #     colander.String(),
        #     widget=deform.widget.HiddenWidget(),
        #     default=request.session['userdata']['lastname'],
        #     missing='',
        #     oid="lastname",
        # )
        # email = colander.SchemaNode(
        #     colander.String(),
        #     widget=deform.widget.HiddenWidget(),
        #     default=request.session['userdata']['email'],
        #     missing='',
        #     oid="email",
        # )
        # _LOCALE_ = colander.SchemaNode(
        #     colander.String(),
        #     widget=deform.widget.HiddenWidget(),
        # )

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
        if not appstruct['ticket']['ticket_gv'] == 2:
            representation = None
        tshirt = TshirtData(
            title=_(u"T-Shirt"),
            oid="tshirt-data"
        )
        if not appstruct['ticket']['ticket_tshirt']:
            tshirt = None

    schema = TicketForm()
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
                'formerror': True
            }
    _html = form.render()

    return {
        'ticket': _ticket,
        'form': _html,
    }
