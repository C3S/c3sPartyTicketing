# -*- coding: utf-8 -*-
"""
This module holds views with accountants functionality.

Staff can

* check statistics (**stats_view**)
"""
from pyramid.view import view_config

from c3spartyticketing.models import (
    PartyTicket,
)


@view_config(renderer='templates/stats.pt',
             permission='manage',
             route_name='stats')
def stats_view(request):
    """
    This view lets accountants view statistics:
    how many tickets of which category, payment status, etc.
    """
    # print("who is it? %s" % request.user.login)

    stats = {}

    # ## General
    stats['general'] = PartyTicket.get_stats_general()

    # ## Events
    stats['events'] = PartyTicket.get_stats_events()

    # ## Extras
    stats['extras'] = PartyTicket.get_stats_extras()

    # ## Abrechnung
    stats['accounting'] = {}
    # Bestellung
    stats['accounting']['order'] = {
        'sum_tickets_total': PartyTicket.get_sum_tickets_total(),
        'sum_tickets_unpaid': PartyTicket.get_sum_tickets_unpaid(),
        'sum_tickets_paid': PartyTicket.get_sum_tickets_paid(),
        'sum_tickets_paid_desk': PartyTicket.get_sum_tickets_paid_desk(),
    }

    # Tickets
    # stats['accounting']['tickets'] = {
    # 'sum_tickets_preorder_cash': PartyTicket.get_sum_tickets_preorder_cash(),
    # 'sum_tickets_new_cash': PartyTicket.get_sum_tickets_new_cash(),
    # 'num_passengers_paid_checkedin':
    #                        PartyTicket.get_num_passengers_paid_checkedin(),
    # }

    # _number_of_tickets = PartyTicket.get_num_tickets()
    # _num_passengers = PartyTicket.num_passengers()
    # _num_open_tickets = int(_number_of_tickets) - int(_num_passengers)
    # _num_tickets_unpaid = PartyTicket.get_num_unpaid()

    return {
        'stats': stats
    }
