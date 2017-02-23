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


def ticket_member_gvonly_schema(request, appstruct, readonly=False):
    """
    A Schema for the Member Ticket Form. GV only.

    Args:
        request: the current request.
        appstruct: a data structure containing user/ticket data.
        readonly: decides whether form is editable or not.


    * comes with a validator

    """

    # ### validator

    def validator(form, value):
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
    # ticket_support_options = ticket_options.get_ticket_support_options(
    #    request)

    # ## formparts

    class TicketGvonlyData(colander.MappingSchema):
        """
        A Colander Schema for GV only Ticket Data.
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
                Download authorization form:
                <a href='https://url.c3s.cc/auprivater' target='_blank'>
                    for regular members,
                </a>
                <a href='https://url.c3s.cc/auprivatei' target='_blank'>
                    for investing members,
                </a>
                <a href='https://url.c3s.cc/aucorporate' target='_blank'>
                    for corporations
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
                Du darfst als Deine(n) Abstimmungs-Bevollmächtigten nur ein
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
                Download für den Vordruck einer Abstimmungs-Vollmacht:
                <a href='http://url.c3s.cc/vmprivato' target='_blank'>
                    Für ordentliche Mitglieder,
                </a>
                <a href='http://url.c3s.cc/vmprivati' target='_blank'>
                    für investierende Mitglieder,
                </a>
                <a href='http://url.c3s.cc/vmkoerperschaft' target='_blank'>
                    für Körperschaften
                </a>

            </div>''',
                oid='rep-note'
            )
        note_bottom.missing = note_bottom.default  # otherwise empty on reedit
        if readonly:
            note_bottom = None

    # ## form

    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Ticketing Information
        - Representation Data
        """
        gvonlynote = colander.SchemaNode(
            colander.String(),
            title='',
            widget=deform.widget.TextInputWidget(
                readonly=True,
                readonly_template="forms/textinput_htmlrendered.pt"
            ),
            default=u'''
            <div class="alert alert-info" role="alert">
                <br />
                There's no option to register for the BarCamp anymore.
                However, you may
                still register for attending the general assembly.
                Participation is free. For organizational reasons, we are
                strongly recommending to register immediately.<br />
                <br />
                There is no option to buy tickets for the BarCamp at the door.
            </div>''',
            missing='',
            oid='gvonly-note'
        )
        if get_locale_name(request) == 'de':
            gvonlynote = colander.SchemaNode(
                colander.String(),
                title='',
                widget=deform.widget.TextInputWidget(
                    readonly=True,
                    readonly_template="forms/textinput_htmlrendered.pt"
                ),
                default=u'''
            <div class="alert alert-info" role="alert">
                <br />
                Die Möglichkeit zur Anmeldung fürs Barcamp
                besteht leider nicht mehr.
                Für die Generalversammlung kannst Du Dich jedoch nach wie
                vor anmelden. Die Teilnahme ist kostenlos. Wir bitten Dich
                aber, Dich aus Planungsgründen umgehend anzumelden.<br />
                <br />
                Für das Barcamp besteht keine Möglichkeit, ein Ticket direkt
                vor Ort zu kaufen.
            </div>''',
                missing='',
                oid='gvonly-note'
            )
        gvonlynote.missing = gvonlynote.default  # otherwise empty on redit
        if readonly:
            gvonlynote = None

        ticket = TicketGvonlyData(
            title=_(u"Ticket Information"),
            oid="ticket-data",
        )

        representation = RepresentationData(
            title=_(u"Representative"),
            oid="rep-data",
        )
        if readonly and not appstruct['ticket']['ticket_gv'] == 2:
            representation = None

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
                "Submit & Buy" below. If you have any questions
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
                Formular keine Änderung mehr vornehmen. Falls Du
                Fragen zu Deiner Bestellung hast, wende Dich bitte an
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
