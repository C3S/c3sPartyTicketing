# -*- coding: utf-8 -*-
"""
This module holds functionality used by views with autocomplete forms.


* list all existing ticket codes (**list_codes**).
* list all existing names (**list_names**).
"""

from pyramid.view import view_config

from c3spartyticketing.models import PartyTicket


@view_config(renderer='json',
             # permission='manage',  # XXX make this work w/ permission
             route_name='all_codes')
def list_codes(request):
    """
    return the list of codes

    Returns:
        JSON
    """
    if 'localhost' not in request.host:
        print(request.host)
        return 'foo'
    codes = PartyTicket.get_all_codes()
    return codes


@view_config(renderer='json',
             # permission='manage',  # XXX make this work w/ permission
             route_name='all_names')
def list_names(request):
    """
    return the list of names

    Returns:
        JSON
    """
    if 'localhost' not in request.host:
        print(request.host)
        return 'foo'
    names = PartyTicket.get_all_names()
    return names
