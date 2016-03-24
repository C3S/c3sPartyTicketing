# -*- coding: utf-8 -*-
"""
This module holds the schema for tickets for nonmembers

It is actually a function that returns a form.

"""
import colander
import deform
from pyramid.i18n import (
    get_locale_name,
    TranslationStringFactory,
)

from c3spartyticketing import ticket_options

_ = TranslationStringFactory('c3spartyticketing')


def ticket_nonmember_schema(request, appstruct, readonly=False):
    """
    A Schema for the Non-Member Ticket Form.

    Args:
        request: the current request.
        appstruct: a data structure containing user/ticket data.
        readonly: decides whether form is editable or not.


    * comes with a validator

    """

    # ## validator

    def validator(form, value):
        """
        checks things...
        """
        # XXX: herausfinden, wie man per klassenvalidator colander.Invalid
        #      ansprechen muss, damit deform den error am richtigen ort
        #      platziert und die richtigen klassen vergibt
        # node.raise_invalid()?
        # add exc as child?
        # #form.raise_invalid('test', form.get('tshirt').get('tshirt_size'))
        # if value['ticket']['ticket_tshirt']:
        #     if not value['tshirt']['tshirt_type']:
        #         raise colander.Invalid(
        #             form,
        #             _(u'Gender selection for T-shirt is mandatory.')
        #         )
        #     if not value['tshirt']['tshirt_size']:
        #         raise colander.Invalid(
        #             form,
        #             _(u'Size of T-shirt ist mandatory.')
        #         )
        # no option set raises an exception
        if (
                ('attendance' not in value['ticket']['ticket_bc']) and
                # (not value['ticket']['ticket_tshirt']) and
                (not value['ticket']['ticket_support'])):
            raise colander.Invalid(
                form,
                _(u'You need to select at least one option.')
            )

    # ## options

    ticket_bc_options = ticket_options.get_ticket_bc_options(request)
    ticket_support_options = ticket_options.get_ticket_support_options(
        request)

    # ## formparts

    class PersonalData(colander.MappingSchema):

        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"First Name"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"Last Name"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u"E-mail"),
            widget=deform.widget.TextInputWidget(
                readonly=readonly
            ),
            validator=colander.Email(),
            oid="email",
        )

    class TicketData(colander.MappingSchema):

        locale_name = get_locale_name(request)
        ticket_bc = colander.SchemaNode(
            colander.Set(),
            title=_(u"BarCamp:"),
            widget=deform.widget.CheckboxChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_bc_options,
                readonly=readonly
            ),
            missing='',
            oid="ticket_bc"
        )
        if readonly:
            ticket_bc.description = None
            if not appstruct['ticket']['ticket_bc']:
                ticket_bc = None
        # ticket_tshirt = colander.SchemaNode(
        #     colander.Boolean(),
        #     title=_(u"Extras:"),
        #     widget=deform.widget.CheckboxWidget(
        #         readonly=readonly,
        #         readonly_template='forms/checkbox_label.pt'
        #     ),
        #     label="T-shirt (€25)",
        #     missing='',
        #     description=_(
        #         u'There will be one joint T-shirt design for both events in '
        #         u'C3S green, black and white. Exclusively for participants, '
        #         u'available only if pre-ordered! You can collect your '
        #         u'pre-ordered T-shirt at both the BarCamp and the general '
        #         u'assembly. If you chose to order a shirt, '
        #         u'you can specify its size below.'
        #     ),
        #     oid="ticket_tshirt"
        # )
        # if readonly:
        #     ticket_tshirt.description = None
        #     if not appstruct['ticket']['ticket_tshirt']:
        #         ticket_tshirt = None
        ticket_support = colander.SchemaNode(
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
                u'other options. They help the cooperative to '
                u'bear the costs occasioned by the events. '
                u'You may choose more than one supporter ticket. '
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
                    u'Your order has to be fully paid by 09.04.2016 at the '
                    u'latest (payment receipt on our account applies)'
                    u'Otherwise we will have to cancel the entire order. '
                    u'Money transfer is the only payment method. Payment '
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
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=locale_name
        )

    # class TshirtData(colander.MappingSchema):
    #     """
    #     colander schema of tshirt form
    #     """
    #     tshirt_type = colander.SchemaNode(
    #         colander.String(),
    #         title=_(u"Gender:"),
    #         widget=deform.widget.RadioChoiceWidget(
    #             size=1, css_class='ticket_types_input',
    #             values=tshirt_type_options,
    #             readonly=readonly
    #         ),
    #         missing=0,
    #         oid="tshirt-type",
    #     )
    #     tshirt_size = colander.SchemaNode(
    #         colander.String(),
    #         title=_(u"Size:"),
    #         widget=deform.widget.RadioChoiceWidget(
    #             size=1, css_class='ticket_types_input',
    #             values=tshirt_size_options,
    #             readonly=readonly
    #         ),
    #         missing=0,
    #         oid="tshirt-size",
    #     )

    # ## form

    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Ticketing Information
        - Representation Data
        """
        personal = PersonalData(
            title=_(u"Personal Data"),
            oid="personal-data",
        )
        ticket = TicketData(
            title=_(u"Ticket Information"),
            oid="ticket-data",
        )
        # tshirt = TshirtData(
        #    title=_(u"T-Shirt"),
        #    oid="tshirt-data"
        # )
        # if readonly and not appstruct['ticket']['ticket_tshirt']:
        #    tshirt = None
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
                "Submit & Buy" below. A full refund of your
                money once transferred is not possible. Only in case the
                BarCamp is cancelled by C3S SCE a refund for the 
                food is possible. If you have any questions please contact
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
                Formular keine Änderung mehr vornehmen. Eine
                Erstattung der überwiesenen Summe ist nicht möglich. Nur
                im Fall der Absage des Barcamps durch die C3S SCE werden
                die Kosten für das Essen erstattet. Falls Du Fragen
                zu Deiner Bestellung hast, wende Dich bitte an
                <a href="mailto:office@c3s.cc" class="alert-link">
                    office@c3s.cc
                </a>
            </div>''',
                missing='',
                oid='final-note'
            )
        finalnote.missing = finalnote.default  # otherwise empty on re-edit
        if not readonly:
            finalnote = None

    return TicketForm(validator=validator).bind()
