"""
This module holds the locators.
"""

from webutils import (
    Server,
    Client
)

locators = {}
server = Server()
client = Client()


# ### member

# fields
locators["ticket.member.token"] = "token"
locators["ticket.member.firstname"] = "firstname"
locators["ticket.member.lastname"] = "lastname"
locators["ticket.member.email"] = "email"
locators["ticket.member.generalassembly"] = "ticket_gv"
locators["ticket.member.barcamp"] = "ticket_bc-0"
locators["ticket.member.buffet"] = "ticket_bc-1"
locators["ticket.member.tshirt"] = "ticket_tshirt"
locators["ticket.member.allinc"] = "ticket_all"
locators["ticket.member.support"] = "ticket_support-0"
locators["ticket.member.supportl"] = "ticket_support-1"
locators["ticket.member.supportxl"] = "ticket_support-2"
locators["ticket.member.supportxxl"] = "ticket_support-3"
locators["ticket.member.comment"] = "comment"
locators["ticket.member.rep.firstname"] = "rep-firstname"
locators["ticket.member.rep.lastname"] = "rep-lastname"
locators["ticket.member.rep.email"] = "rep-email"
locators["ticket.member.rep.street"] = "rep-street"
locators["ticket.member.rep.zip"] = "rep-zip"
locators["ticket.member.rep.city"] = "rep-city"
locators["ticket.member.rep.country"] = "rep-country"
locators["ticket.member.rep.firstname"] = "rep-firstname"
locators["ticket.member.rep.type"] = "rep-type"
# locators["ticket.member.tshirt.type"] = "tshirt-type"
# locators["ticket.member.tshirt.size"] = "tshirt-size"

# buttons
locators["ticket.member.ticket.submit"] = "deformsubmit"
locators["ticket.member.confirm.reedit"] = "deformreedit"
locators["ticket.member.confirm.confirm"] = "deformconfirmed"


# ### nonmember

# fields
locators["ticket.nonmember.firstname"] = "firstname"
locators["ticket.nonmember.lastname"] = "lastname"
locators["ticket.nonmember.email"] = "email"
locators["ticket.nonmember.barcamp"] = "ticket_bc-0"
locators["ticket.nonmember.buffet"] = "ticket_bc-1"
locators["ticket.nonmember.tshirt"] = "ticket_tshirt"
locators["ticket.nonmember.support"] = "ticket_support-0"
locators["ticket.nonmember.supportl"] = "ticket_support-1"
locators["ticket.nonmember.supportxl"] = "ticket_support-2"
locators["ticket.nonmember.supportxxl"] = "ticket_support-3"
locators["ticket.nonmember.comment"] = "comment"
# locators["ticket.nonmember.tshirt.type"] = "tshirt-type"
# locators["ticket.nonmember.tshirt.size"] = "tshirt-size"

# buttons
locators["ticket.nonmember.ticket.submit"] = "deformsubmit"
locators["ticket.nonmember.confirm.reedit"] = "deformreedit"
locators["ticket.nonmember.confirm.confirm"] = "deformconfirmed"
