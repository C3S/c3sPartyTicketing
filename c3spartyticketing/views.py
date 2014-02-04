# -*- coding: utf-8 -*-

from c3spartyticketing.models import (
    DBSession,
    PartyTicket,
)
from c3spartyticketing.utils import (
    make_qr_code_pdf,
    make_qr_code_pdf_mobile,
)
import colander
from datetime import datetime
import deform
from deform import ValidationFailure
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

#from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import (
    InvalidRequestError,
    IntegrityError
)
from types import NoneType
#from translationstring import TranslationStringFactory
_ = TranslationStringFactory('c3spartyticketing')

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


@view_config(route_name='party', renderer='templates/party.pt')
def party_view(request):
    """
    the view users use to order a ticket
    """
    _num_tickets = PartyTicket.get_num_tickets()
    _num_tickets_paid = PartyTicket.get_num_tickets_paid()

    class PersonalData(colander.MappingSchema):
        """
        colander schema for membership application form
        """
        locale_name = get_locale_name(request)
        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"Vorame"),
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"Nachname"),
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u'Email'),
            validator=colander.Email(),
            oid="email",
        )
        # password = colander.SchemaNode(
        #     colander.String(),
        #     validator=colander.Length(min=3, max=100),
        #     widget=deform.widget.PasswordWidget(size=20),
        #     title=_(u"Password (to protect access to your data)"),
        #     description=_("We need a password to protect your data. After "
        #                   "verifying your email you will have to enter it."),
        #     oid="password",
        # )
        comment = colander.SchemaNode(
            colander.String(),
            title=_("Kommentare"),
            missing='',
            validator=colander.Length(max=250),
            widget=deform.widget.TextAreaWidget(rows=3, cols=50),
            description=_(u"Raum für Kommentare"),
            oid="comment",
        )
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.HiddenWidget(),
            default=locale_name
        )

    num_ticket_options = (
        ('10', _(u'10 tickets')),
        ('9', _(u'9 tickets')),
        ('8', _(u'8 tickets')),
        ('7', _(u'7 tickets')),
        ('6', _(u'6 tickets')),
        ('5', _(u'5 tickets')),
        ('4', _(u'4 tickets')),
        ('3', _(u'3 tickets')),
        ('2', _(u'2 tickets')),
        ('1', _(u'1 tickets')),
        #('0', _(u'no ticket')),
    )
    ticket_type_options = (
        (1, _(u'2. Klasse (5€: party, bands)')),
        (2, _(u'2. Klasse + Speisewagen (15€: party, bands, essen)')),
        (3, _(u'1. Klasse (50€: party, bands, essen, kaffee, shirt)')),
        (4, _(u'Grüne Mamba (100€: party, bands, essen, kaffee, jacke)')),
    )

    class PartyTickets(colander.MappingSchema):

        ticket_type = colander.SchemaNode(
            colander.Integer(),
            title=_(u"Ich reise in der folgenden Kategorie:"),
            description=_(
                u'Du kannst uns mit dem Kauf von Tickets unterstützen. '
                u'Überschüsse fliessen in die Büroausstattung.'),
            default="1",
            widget=deform.widget.RadioChoiceWidget(
                size=1, css_class='ticket_types_input',
                values=ticket_type_options,
                #inline=True
            ),
            oid="ticket_type"
        )
        num_tickets = colander.SchemaNode(
            colander.Integer(),
            title=_(u"Ich nehme die folgende Anzahl von Tickets"),
            description=_(
                u'Du kannst zwischen 1 und 10 Tickets bestellen. '
                u'Die Kosten variieren je nach Ticket-Kategorie.'),
            default="1",
            widget=deform.widget.SelectSliderWidget(
                #size=3, css_class='num_tickets_input',
                values=num_ticket_options),
            validator=colander.Range(
                min=1,
                max=10,
                min_err=_(u"Du brauchst mindestens ein Ticket, "
                          u"um die Reise anzutreten."),
                max_err=_(u"Höchstens 10 Tickets. (viel los!)"),
            ),
            oid="num_tickets")

    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Personal Data
        - Ticketing Information
        - FoodInfo
        """
        person = PersonalData(
            title=_(u"Persönliche Daten"),
            #description=_(u"this is a test"),
            #css_class="thisisjustatest"
        )
        ticket_info = PartyTickets(
            title=_(u"Ticketinformationen")
        )
        #shares = FoodInfo(
        #    title=_(u"Food Stamps")
        #)

    schema = TicketForm()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Absenden')),
            deform.Button('reset', _(u'Zurücksetzen'))
        ],
        use_ajax=True,
        renderer=zpt_renderer
    )

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
                print("the thing: %s") % thing
                print("type: %s") % type(thing)

        except ValidationFailure, e:
            print(e)
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{
                'form': e.render(),
                '_num_tickets': _num_tickets,
                '_num_tickets_paid': _num_tickets_paid,
            }

        from c3spartyticketing.utils import make_random_string
        # make confirmation code
        randomstring = make_random_string()

        # calculate the total sum
        the_value = {
            1: 5,
            2: 15,
            3: 50,
            4: 100,
        }
        _the_total = appstruct['ticket_info']['num_tickets'] * the_value.get(
            appstruct['ticket_info']['ticket_type'])
        appstruct['ticket_info']['the_total'] = _the_total
        print("_the_total: %s" % _the_total)
        # to store the data in the DB, an object is created
        ticket = PartyTicket(
            firstname=appstruct['person']['firstname'],
            lastname=appstruct['person']['lastname'],
            email=appstruct['person']['email'],
            password='',  # appstruct['person']['password'],
            locale=appstruct['person']['_LOCALE_'],
            email_is_confirmed=False,
            email_confirm_code=randomstring,
            date_of_submission=datetime.now(),
            num_tickets=appstruct['ticket_info']['num_tickets'],
            ticket_type=appstruct['ticket_info']['ticket_type'],
            the_total=_the_total,
            user_comment=appstruct['person']['comment'],
        )
        dbsession = DBSession
        try:
            print "about to add ticket"
            dbsession.add(ticket)
            print "adding ticket"
            appstruct['email_confirm_code'] = randomstring  # XXX
            appstruct['email_confirm_code'] = randomstring
        except InvalidRequestError, e:  # pragma: no cover
            print("InvalidRequestError! %s") % e
        except IntegrityError, ie:  # pragma: no cover
            print("IntegrityError! %s") % ie

        # redirect to success page, then return the PDF
        # first, store appstruct in session
        request.session['appstruct'] = appstruct
        request.session['appstruct']['_LOCALE_'] = appstruct['person']['_LOCALE_']
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
            form.set_appstruct(appstruct)
            #import pdb
            #pdb.set_trace()
            #form = deform.Form(schema,
            #           buttons=[deform.Button('submit', _(u'Submit'))],
            #           use_ajax=True,
            #           renderer=zpt_renderer
            #           )

    html = form.render()
    return {
        'form': html,
        '_num_tickets': _num_tickets,
        '_num_tickets_paid': _num_tickets_paid,
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

    class PersonalData(colander.MappingSchema):
        """
        colander schema for membership application form
        """
        locale_name = get_locale_name(request)
        firstname = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextInputWidget(readonly=True),  # read-only!
            title=_(u"Vorame"),
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextInputWidget(readonly=True),  # read-only!
            title=_(u"Nachame"),
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextInputWidget(readonly=True),  # read-only!
            title=_(u'Email'),
            validator=colander.Email(),
            oid="email",
        )
        comment = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextInputWidget(readonly=True),  # read-only!
            title=_(u"Kommentar"),
            #description=_("Please leave a message after the beep!"),
            oid="comment",
        )

    class PartyTickets(colander.MappingSchema):

        ticket_type_options = (
            (1, _(u'2. Klasse (5€: party, bands)')),
            (2, _(u'2. Klasse + Speisewagen (15€: party, bands, essen)')),
            (3, _(u'1. Klasse (50€: party, bands, essen, kaffee, shirt)')),
            (4, _(u'Grüne Mamba (100€: party, bands, essen, kaffee, jacke)')),
        )

        ticket_type = colander.SchemaNode(
            colander.Integer(),
            title=_(u"Ich wähle folgende Ticket-Option:"),
            description=_(
                u'Wir danken für die Unterstützung. Hinweis: '
                u'Überschüsse gehen in die Büroausstattung.'),
            default="1",
            widget=deform.widget.RadioChoiceWidget(
                readonly=True,
                size=1, css_class='ticket_types_input',
                values=ticket_type_options,
                #inline=True
            ),
            oid="ticket_type"
        )
        num_tickets = colander.SchemaNode(
            colander.Integer(),
            title=_(u"Ich möchte diese Anzahl Tickets:"),
            default="1",
            widget=deform.widget.TextInputWidget(
                inline=True,
                readonly=True),  # read-only!
            oid="num_tickets"
        )

        the_total = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextInputWidget(readonly=True),  # read-only!
            default=str(
                request.session['appstruct']['ticket_info']['the_total']
            ) + u"&euro;",
            title=_(u"Die Summe"),
            description=_(
                u'Das Ticket muß spätestens bis zum 10.02. bezahlt sein '
                u'(Zahlungseingang auf unserem Konto), '
                u'sonst verliert es seine Gültigkeit. '
                u'Die Zahlung erfolgt ausschließlich per Banküberweisung. '
                u'Die Zahlungsinformationen werden dir per Mail zugeschickt.'),
            oid="summe",
        )

    class TicketForm(colander.Schema):
        """
        The Form consists of
        - Personal Data
        - Ticketing Information
        - FoodInfo
        """
        person = PersonalData(
            title=_(u"Persönliche Daten"),
            #description=_(u"this is a test"),
            #css_class="thisisjustatest"
        )
        ticket_info = PartyTickets(
            title=_(u"Ticket Informationen")
        )

    ro_schema = TicketForm()

    ro_form = deform.Form(
        ro_schema,
        buttons=[
            deform.Button('sendmail',
                          _(u'Ja, schick mir eine Email!')),
            deform.Button('reedit',
                          _(u'Warte, ich will nochmal ändern...'))
        ],
        use_ajax=True,
        renderer=zpt_renderer
    )

    return {
        'readonlyform': ro_form.render(
            appstruct=request.session['appstruct'])}


@view_config(route_name='sendmail',
             renderer='templates/sendmail.pt')
def sendmail_view(request):
    """
    this view sends a mail to the user and tells her to transfer money
    """
    if 'appstruct' in request.session:
        appstruct = request.session['appstruct']

        # save ticketing info in DB
        #   rather do it here than over in the confirm_view
        #   because the information is still subject to change there,
        #   so we get duplicates

        # send email
        mailer = get_mailer(request)
        body_lines = (  # a list of lines
            _(u'Hallo'), ' ', appstruct['person']['firstname'], ' ',
            appstruct['person']['lastname'], u''' !

Wir haben Deine Ticketbestellung erhalten. Bitte überweise jetzt ''',
            str(appstruct['ticket_info']['the_total']) + u''' Euro
auf unser Konto bei der

EthikBank eG
Kontoinhaber: C3S SCE
Betrag (€): ''' + str(appstruct['ticket_info']['the_total']) + u'''
Verwendungszweck: Party ''' + appstruct['email_confirm_code'] + u'''
BIC:\t GENO DE F1 ETK
IBAN:\t DE79830944950003264378
oder
Kontonummer: 3264378
BLZ: 83094495

Sobald wir den Eingang der Zahlung bemerken, schicken wir Dir eine Email mit
dem (oder den) Ticket(s).
''',
            _(u"Bis bald!"), u'''

''',
            _(u"Dein C3S-Team"),
        )
        the_mail_body = ''.join([line for line in body_lines])
        the_mail = Message(
            subject=_(u"C3S Party-Ticket: bitte überweisen!"),
            sender="noreply@c3s.cc",
            recipients=[appstruct['person']['email']],
            body=the_mail_body
        )
        mailer.send(the_mail)
        #print(the_mail.body)
        from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
        # send mail to accountants
        acc_mail = Message(
            subject=_('[C3S_PT] neues ticket'),
            sender="noreply@c3s.cc",
            recipients=[
                request.registry.settings['c3spartyticketing.mail_rec']],
            #body=encrypt_with_gnupg('''code: %s
            body=u'''code: %s
klass: %s
number: %s
total: %s
komment: %s
''' % (appstruct['email_confirm_code'],
       appstruct['ticket_info']['ticket_type'],
       appstruct['ticket_info']['num_tickets'],
       appstruct['ticket_info']['the_total'],
       appstruct['person']['comment'],
       )
        )
        mailer.send(acc_mail)
        # make the session go away
        request.session.invalidate()
        return {
            'firstname': appstruct['person']['firstname'],
            'lastname': appstruct['person']['lastname'],
        }
    # 'else': send user to the form
    return HTTPFound(location=request.route_url('party'))


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
