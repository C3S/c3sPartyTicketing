# -*- coding: utf-8 -*-

# from pyramid.i18n import TranslationStringFactory

# _ = TranslationStringFactory('c3spartyticketing')

from c3spartyticketing.views import _


def get_ticket_gv_options(request):
    """
    Options for the General Assembly.
    """
    ticket_gv_options = (
        (1, _(u'I will attend the C3S SCE General Assembly.')),
        (2, _(
            u'I will not attend the C3S SCE General Assembly personally. '
            u'I will be represented by an authorized person.'
        )),
        (3, _(u'I will not attend the C3S SCE General Assembly.'))
    )
    return ticket_gv_options

    # ticket_gv_food_option = (
    #    ('buffet', _(
    #        u'I\'d like to have Coffee and Cake during '
    #        u' and a cooked meal after the BarCamp. (€12)'))
    # )
    # """
    # Food Options for the General Assembly.
    # """


def get_rep_type_options():
    """
    Options for choosing a Representative.
    """
    return (
        ('member', _(u'a member of C3S SCE')),
        ('partner', _(u'my spouse / registered civil partner')),
        ('parent', _(u'my parent')),
        ('child', _(u'my child')),
        ('sibling', _(u'my sibling'))
    )
    

def get_ticket_bc_options(request):
    """
    Options for BarCamp Tickets.
    """
    ticket_bc_options = (
        ('attendance', (_(u"I will attend the BarCamp. (€0)"))),  #  + u' (€{})foo'.format(request.bc_cost))),
        ('buffet', (_(
            u"I'd like to have coffee and cake during "
            u"and buffet after the BarCamp. (€12)")))  #  + u' (€{})'.format(request.bc_food_cost)))
    )
    return ticket_bc_options


def get_ticket_support_options(request):
    """
    Supporter Ticket Options.
    """
    ticket_support_options = (
        (1, _(u'Supporter Ticket (€5)')),
        (2, _(u'Supporter Ticket L (€10)')),
        (3, _(u'Supporter Ticket XL (€20)')),
        (4, _(u'Supporter Ticket XXL (€50)')),
    )
    return ticket_support_options


# tshirt_type_options = (
#     ('m', _(u'male')),
#     ('f', _(u'female'))
# )

# tshirt_size_options = (
#     ('S', _(u'S')),
#     ('M', _(u'M')),
#     ('L', _(u'L')),
#     ('XL', _(u'XL')),
#     ('XXL', _(u'XXL')),
#     ('XXXL', _(u'XXXL'))
# )


def get_guest_options_bc():
    guest_options_bc = (
        ('', ''),
        ('helper', 'Helfer'),
        ('guest', 'Gast'),
        ('specialguest', 'Ehrengast'),
        ('press', 'Presse'),
    )
    return guest_options_bc


def get_guest_options_gv():
    guest_options_gv = (
        ('', ''),
        ('helper', 'Helfer'),
        ('guest', 'Gast'),
        ('specialguest', 'Ehrengast'),
        ('press', 'Presse'),
        ('representative', 'Repräsentant'),
    )
    return guest_options_gv


def get_membership_type_options():
    membership_type_options = (
        ('nonmember', 'Nicht-Mitglied'),
        ('normal', 'Normal'),
        ('investing', 'Investierend'),
    )
    return membership_type_options


def get_locale_options():
    locale_options = (
        ('de', 'deutsch'),
        ('en', 'englisch'),
    )
    return locale_options
