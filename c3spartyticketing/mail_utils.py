# -*- coding: utf-8 -*-
"""
Compiles email texts for payment confirmation and signature confirmation
emails.
"""
import os


LOCALE_DEFINITIONS = {
    'de': {
        'date_format': '%d.%m.%Y',
        'time_format': '%H:%M',
    },
    'en': {
        'date_format': '%d %b %Y',
        'time_format': '%H%p'
    },
}


def get_locale(locale):
    return locale if locale in LOCALE_DEFINITIONS else 'en'


def get_template_text(template_name, locale):
    return open(
        '{base_path}/templates/mails/{template_name}_{locale}.txt'.format(
            base_path=os.path.dirname(__file__),
            template_name=template_name,
            locale=get_locale(locale)),
        'rb').read().decode('utf-8')


def get_salutation(member):
    """
    Returns:
       unicode: salutation for person or legal entity
    """
    if member.is_legalentity:
        # for legal entites the firstname attribute contains the name of the
        # contact person of the legal entity while the lastname attribute
        # contains the legal entity's name
        return member.firstname
    else:
        return u'{first_name} {last_name}'.format(
            first_name=member.firstname,
            last_name=member.lastname)


def format_date(date, locale):
    """
    Returns:
       date string: given date, formatted according to given locale
    """
    return date.strftime(
        LOCALE_DEFINITIONS[get_locale(locale)]['date_format'])


def format_time(time, locale):
    """
    Returns:
       time string: given time, formatted according to given locale
    """
    # print("the locale: {}".format(locale))
    return time.strftime(
        LOCALE_DEFINITIONS[get_locale(locale)]['time_format'])


def get_email_footer(locale):
    """
    Returns:
       multiline string: reusable email footer
    """
    return get_template_text('email_footer', locale)


def make_ticket_email(request, ticket):
    """
    Gets an email subject and body to deliver links to the ticket PDFs.
    """
    return (
        get_template_text('ticketmail_subject', ticket.locale),
        get_template_text('ticketmail_body', ticket.locale).format(
            salutation=get_salutation(ticket),
            ticket_email_confirm_code=ticket.email_confirm_code,
            ticket_url_mobile=request.route_url(
                'get_ticket_mobile',
                email=ticket.email,
                code=ticket.email_confirm_code),
            ticket_url=request.route_url(
                'get_ticket',
                email=ticket.email,
                code=ticket.email_confirm_code),
            footer=get_email_footer(ticket.locale)))


def make_payment_reception_email(request, ticket):
    """
    Gets an email subject and body to confirm reception of payment.
    """
    return (
        get_template_text('payment_reception_email_subject', ticket.locale).rstrip(),
        get_template_text(
            'payment_reception_email_body',
            ticket.locale).format(
                salutation=get_salutation(ticket),
                footer=get_email_footer(ticket.locale)))
