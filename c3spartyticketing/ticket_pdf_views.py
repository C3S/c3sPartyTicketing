# -*- coding: utf-8 -*-
"""
This module holds views with functionality to produce tickets: mobile/printout.
"""
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from types import NoneType

from c3spartyticketing.utils import (
    make_qr_code_pdf,
    make_qr_code_pdf_mobile,
)
from c3spartyticketing.models import (
    PartyTicket,
)


@view_config(route_name='get_ticket')
def get_ticket(request):
    """
    This view gives a user access to her ticket via URL with code.

    === =================================================================
    URL http/s://app:port/ticket/email%40example.com/C3S_Ticket_TOKENCODE
    === =================================================================

    Returns:
        a PDF download
    """
    _code = request.matchdict['code']
    _email = request.matchdict['email']
    _ticket = PartyTicket.get_by_code(_code)
    if isinstance(_ticket, NoneType):
        return HTTPFound(location=request.route_url('party'))
    if not (_ticket.email == _email):
        # print("no match!")
        return HTTPFound(location=request.route_url('party'))

    # prepare ticket URL with email & code
    # 'https://events.c3s.cc/ci/p1402/'
    #          + _ticket.email + _ticket.email_confirm_code
    # 'https://192.168.2.128:6544/ci/p1402/'
    #          + _ticket.email + _ticket.email_confirm_code
    _url = request.registry.settings[
        'c3spartyticketing.url'] + '/ci/' + \
        request.registry.settings['eventcode'] + \
        '/' + _ticket.email_confirm_code

    # return a pdf file
    pdf_file = make_qr_code_pdf(_ticket, _url)
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")
    return response


@view_config(route_name='get_ticket_mobile')
def get_ticket_mobile(request):
    """
    This view gives a user access to her ticket via URL with code.

    === ==================================================================
    URL http/s://app:port/mticket/email%40example.com/C3S_Ticket_TOKENCODE
    === ==================================================================

    Returns:
        a PDF download
    """
    _code = request.matchdict['code']
    _email = request.matchdict['email']
    _ticket = PartyTicket.get_by_code(_code)
    if isinstance(_ticket, NoneType):
        return HTTPFound(location=request.route_url('party'))
    if not (_ticket.email == _email):
        # print("no match!")
        return HTTPFound(location=request.route_url('party'))

    # prepare check-in URL for qr-code
    _url = request.registry.settings[
        'c3spartyticketing.url'] + '/ci/' \
        + request.registry.settings['eventcode'] \
        + '/' + _ticket.email_confirm_code

    # return a pdf file
    pdf_file = make_qr_code_pdf_mobile(_ticket, _url)
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")
    return response
