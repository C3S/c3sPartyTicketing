# -*- coding: utf-8 -*-

from datetime import date
from pyramid.view import view_config

from c3spartyticketing.models import PartyTicket


@view_config(renderer='templates/ticket_list_ga.pt',
             permission='manage',
             route_name='ticket_listing_ga_printout')
def ticket_list_ga_print_view(request):
    _order_by = 'lastname'
    _num = PartyTicket.get_number()
    _tickets = PartyTicket.ticket_listing_ga(
        _order_by, how_many=_num, offset=0)  # , order=u'asc')
    # sort tickets alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    _tickets.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    _tickets.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    _today = date.today()
    return {
        'tickets': _tickets,
        'count': len(_tickets),
        '_today': _today,
    }


@view_config(renderer='templates/ticket_list_bc.pt',
             permission='manage',
             route_name='ticket_listing_bc_printout')
def ticket_list_bc_print_view(request):
    _order_by = 'lastname'
    _num = PartyTicket.get_number()
    _tickets = PartyTicket.ticket_listing_bc(
        _order_by, how_many=_num, offset=0)  # , order=u'asc')
    # sort tickets alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    _tickets.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    _tickets.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    _today = date.today()
    return {
        'tickets': _tickets,
        'count': len(_tickets),
        '_today': _today,
    }


@view_config(renderer='csv',
             permission='manage',
             route_name='ticket_namelist')
def ticket_namelist_view(request):
    _order_by = 'lastname'
    _num = PartyTicket.get_number()
    _tickets = PartyTicket.ticket_listing(
        _order_by, how_many=_num, offset=0)  # , order=u'asc')
    # sort tickets alphabetically
    import locale
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

    _tickets.sort(key=lambda x: x.firstname, cmp=locale.strcoll)
    _tickets.sort(key=lambda x: x.lastname, cmp=locale.strcoll)

    header = [
        'firstname', 'lastname', 'email', 'membership_type',
        'token', 'code', 'locale',
        'gv_attendance', 'checked_gv',
        'bc_attendance', 'checked_bc',
        'bc_buffet',
        'extra1', 'extra2', 'extra3',
        'shirt', 'shirt size', 'shirt type',
        'support', 'support_x', 'support_xl',
        'the_total',
        'rep_firstname', 'rep_lastname', 'rep_street',
        'rep_zip', 'rep_city',
        'rep_country', 'rep_type', 'rep_email',
        'represents_id1', 'represents_id2',
        'guestlist', 'guestlist_gv', 'guestlist_bc',
        'payment_received', 'payment_received_date',
        'user_comment', 'accountant_comment', 'staff_comment'
    ]
    rows = []

    for t in _tickets:
        rows.append(
            (t.firstname, t.lastname, t.email, t.membership_type,
             t.token, t.email_confirm_code, t.locale,
             t.ticket_gv_attendance, t.checked_gv,
             t.ticket_bc_attendance, t.checked_bc,
             t.ticket_bc_buffet,
             t.received_extra1, t.received_extra2, t.received_extra3,
             t.ticket_tshirt, t.ticket_tshirt_size, t.ticket_tshirt_type,
             t.ticket_support, t.ticket_support_x, t.ticket_support_xl,
             t.the_total,
             t.rep_firstname, t.rep_lastname, t.rep_street,
             t.rep_zip, t.rep_city,
             t.rep_country, t.rep_type, t.rep_email,
             t.represents_id1, t.represents_id2,
             t.guestlist, t.guestlist_gv, t.guestlist_bc,
             t.payment_received, t.payment_received_date,
             t.user_comment, t.accountant_comment, t.staff_comment
         )
        )
    return {
        'header': header,
        'rows': rows,
    }
