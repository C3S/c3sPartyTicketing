# -*- coding: utf-8 -*-

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('c3spartyticketing')


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
        ('attendance', _(
            u'I will attend the BarCamp.'
        ) + u' (€{})'.format(request.bc_cost)),
        ('buffet', _(
            u'I\'d like to have coffee and cake during '
            u'and buffet after the BarCamp.'
        ) + u' (€{})'.format(request.bc_food_cost))
    )
    return ticket_bc_options


def get_ticket_support_options(request):
    """
    Supporter Ticket Options.
    """
    ticket_support_options = (
        (1, _(u'Supporter Ticket') + u' (€{})'.format(
            request.supporter_M)),
        (2, _(u'Supporter Ticket L') + u' (€{})'.format(
            request.supporter_L)),
        (3, _(u'Supporter Ticket XL') + u' (€{})'.format(
            request.supporter_XL)),
        (4, _(u'Supporter Ticket XXL') + u' (€{})'.format(
            request.supporter_XXL))
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
