# -*- coding: utf-8 -*-
"""
This module holds the schema for tickets for members (?)

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


def ticket_member_schema(request, appstruct, readonly=False):
    """
    A Schema for the Member Ticket Form.

    Args:
        request: the current request.
        appstruct: a data structure containing user/ticket data.
        readonly: decides whether form is editable or not.


    * comes with a validator

    """
    # ### validator

    def validator(form, value):
        """
        A validator ...
        """
        # XXX: herausfinden, wie man per klassenvalidator colander.Invalid
        #      ansprechen muss, damit deform den error am richtigen ort
        #      platziert und die richtigen klassen vergibt
        # node.raise_invalid()?
        # add exc as child?
        # form.raise_invalid('test', form.get('tshirt').get('tshirt_size'))
        # if value['ticket']['ticket_tshirt']:
        #    if not value['tshirt']['tshirt_type']:
        #        raise colander.Invalid(
        #            form,
        #            _(u'Gender selection for T-shirt is mandatory.')
        #        )
        #    if not value['tshirt']['tshirt_size']:
        #        raise colander.Invalid(
        #            form,
        #            _(u'Size of T-shirt ist mandatory.')
        #        )
        if value['ticket']['ticket_gv'] == 2:
            if not value['representation']['firstname']:
                raise colander.Invalid(
                    form,
                    _(u'First name of representative is mandatory.')
                )
            if not value['representation']['lastname']:
                raise colander.Invalid(
                    form,
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
                raise colander.Invalid(
                    form,
                    _(u'Address of representative is mandatory.')
                )
            if not value['representation']['zip']:
                raise colander.Invalid(
                    form,
                    _(u'Postal code of representative is mandatory.')
                )
            if not value['representation']['city']:
                raise colander.Invalid(
                    form,
                    _(u'City of representative is mandatory.')
                )
            if not value['representation']['country']:
                raise colander.Invalid(
                    form,
                    _(u'Country of representative is mandatory.')
                )
            if not value['representation']['representation_type']:
                raise colander.Invalid(
                    form,
                    _(u'Relation of representative is mandatory.')
                )

    # ## options

    ticket_gv_options = ticket_options.get_ticket_gv_options(request)
    rep_type_options = ticket_options.get_rep_type_options()
    ticket_bc_options = ticket_options.get_ticket_bc_options(request)
    ticket_support_options = ticket_options.get_ticket_support_options(
        request)

    # ### formparts

    class TicketData(colander.MappingSchema):
        """
        A Colander schema for Ticket Data.
        """

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
            oid="ticket_bc"
        )
        if readonly:
            ticket_bc.description = None
            if not appstruct['ticket']['ticket_bc']:
                ticket_bc = None

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
                u'other options. This is a good occasion to support the C3S '
                u'financially. '
                u'You may choose more than one supporter ticket.'
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
                    u'Your order has to be fully paid by 14.04.2016 at the '
                    u'latest (payment receipt on our account applies). '
                    u'Money transfer is the only payment method. Payment '
                    u'information will be sent to you shortly by e-mail.'
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
            oid="token",
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
        Colander schema of respresentation form.
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
        # note_top.default = None
        note_top.missing = note_top.default  # otherwise empty on redit
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
                at most (see § 13 (6), sentence 3, of the 
                <a href='https://url.c3s.cc/statutes' target='_blank'>
                    articles of association
                </a>).
                Registered civil partners are treated as spouses.
                <br>
                <strong>Don't forget:</strong>
                Your representative has to provide an authorization
                certificate signed by you. Please do not bring or send
                a copy, fax, scan, or picture. We can only accept the
                original document.
                <br>
                Download 
                <a href='https://url.c3s.cc/auprivater' target='_blank'>
                authorization form
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
                <a href='https://url.c3s.cc/satzung' target='_blank'>
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
                Download für den 
                <a href='https://url.c3s.cc/vmprivato' target='_blank'>
                    Vordruck einer Vollmacht
                </a>
            </div>''',
                oid='rep-note'
            )
        note_bottom.missing = note_bottom.default  # otherwise empty on reedit
        if readonly:
            note_bottom = None

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

    # ### form

    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Ticketing Information
        - Representation Data
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
            representation = None
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
                    We will send the tickets in time by e-mail
                </strong><br />
                You can't edit the order form after hitting the button
                "Submit & Buy" below. However, you can click the personal
                link you received as part of the invitation link. There you
                can view but not edit your order. A full refund of your
                money once transferred is not possible. Only in case the
                BarCamp is cancelled by C3S SCE a refund for food is 
                possible. If you have any questions please contact
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
                    Wir versenden die Tickets rechtzeitig per Email.
                </strong><br />
                Sobald Du das Bestellformular mit dem Button "Absenden &
                Kaufen" unten absendest, kannst Du an der Bestellung im
                Formular keine Änderung mehr vornehmen. Du kannst Deine
                Bestellung jedoch unter Deinem persönlichen Link aus der
                Einladungs-Mail weiterhin aufrufen und anschauen. Eine
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
        finalnote.missing = finalnote.default  # otherwise empty on redit
        if not readonly:
            finalnote = None

    return TicketForm(validator=validator).bind()
