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
             route_name='match_rep_names')
def match_representatives_names(request):
    """
    return the list of tickets matching a representatives lastname prefix

    Returns:
        JSON
    """
    if 'localhost' not in request.host:
        # print(request.host)
        return 'foo'
    text = request.params.get('term', '')
    print u"DEBUG: autocomp. rep search for: {}".format(text)
    names = PartyTicket.get_matching_names_rep(text)
    return names
