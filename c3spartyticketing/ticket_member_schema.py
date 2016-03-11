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

    ticket_gv_options = (
        (1, _(u'I will attend the C3S SCE General Assembly.')),
        (2, _(
            u'I will not attend the C3S SCE General Assembly personally. '
            u'I will be represented by an authorized person.'
        )),
        (3, _(u'I will not attend the C3S SCE General Assembly.'))
    )
    """
    Options for the General Assembly.
    """

    # ticket_gv_food_option = (
    #    ('buffet', _(
    #        u'I\'d like to have Coffee and Cake during '
    #        u' and a cooked meal after the BarCamp. (€12)'))
    # )
    # """
    # Food Options for the General Assembly.
    # """

    ticket_bc_options = (
        ('attendance', _(u'I will attend the BarCamp.')),
        ('buffet', _(
            u'I\'d like to have Coffee and Cake during '
            u' and a cooked meal after the BarCamp. (€12)'))
    )

    ticket_support_options = (
        (1, _(u'Supporter Ticket (€5)')),
        (2, _(u'Supporter Ticket XL (€10)')),
        (3, _(u'Supporter Ticket XXL (€100)'))
    )
    """
    Supporter Ticket Options.
    """

    rep_type_options = (
        ('member', _(u'a member of C3S SCE')),
        ('partner', _(u'my spouse / registered civil partner')),
        ('parent', _(u'my parent')),
        ('child', _(u'my child')),
        ('sibling', _(u'my sibling'))
    )
    """
    Options for choosing a Representative.
    """

    # tshirt_type_options = (
    #    ('m', _(u'male')),
    #    ('f', _(u'female'))
    # )

    # tshirt_size_options = (
    #     ('S', _(u'S')),
    #     ('M', _(u'M')),
    #     ('L', _(u'L')),
    #     ('XL', _(u'XL')),
    #     ('XXL', _(u'XXL')),
    #     ('XXXL', _(u'XXXL'))
    # )

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
            description=_(
                u'We will try to offer catering for a fixed price. '
                u'There will be Coffee and a snack or cake in the afternoon '
                u'and a cooked meal at the end of the day.'
            ),
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
        #        ticket_tshirt = None
        # ticket_all = colander.SchemaNode(
        #     colander.Boolean(),
        #     title=_(u"Special Offer:"),
        #     widget=deform.widget.CheckboxWidget(
        #         readonly=readonly,
        #         readonly_template='forms/checkbox_label.pt'
        #     ),
        #     label="All-Inclusive (€42)",
        #     missing='',
        #     description=_(
        #         u'The all-inclusive package covers the participation in the '
        #         u'BarCamp (including coffee, cake and a warm meal), '
        #         u'participation in the general assembly. '
        #         # u'and a T-shirt (Supporter) as well.'
        #     ),
        #     oid="ticket_all"
        # )
        # if readonly:
        #    ticket_all.description = None
        #    ticket_all.label = _(u"All-Inclusive Discount (-€2,50)")
        #    if not appstruct['ticket']['ticket_all']:
        #        ticket_all = None
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
        finalnote.missing = finalnote.default  # otherwise empty on redit
        if not readonly:
            finalnote = None

    return TicketForm(validator=validator).bind()
