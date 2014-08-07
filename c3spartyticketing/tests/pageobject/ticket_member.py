from pageobject import locators, client, server
from pageobject.basepageobject import BasePageObject
from pageobject.basepageelement import (
	HiddenElement,
	TextfieldElement,
	TextareaElement,
	CheckboxElement,
	RadiobuttonElement,
	ButtonElement,
)


class TicketMemberObject(BasePageObject):

	token = HiddenElement(locators["ticket.member.token"])
	firstname = HiddenElement(locators["ticket.member.firstname"])
	lastname = HiddenElement(locators["ticket.member.lastname"])
	email = HiddenElement(locators["ticket.member.email"])

	generalassembly = RadiobuttonElement(locators["ticket.member.generalassembly"])
	barcamp = CheckboxElement(locators["ticket.member.barcamp"])
	buffet = CheckboxElement(locators["ticket.member.buffet"])
	tshirt = CheckboxElement(locators["ticket.member.tshirt"])
	allinc = CheckboxElement(locators["ticket.member.allinc"])
	support = CheckboxElement(locators["ticket.member.support"])
	supportxl = CheckboxElement(locators["ticket.member.supportxl"])
	supportxxl = CheckboxElement(locators["ticket.member.supportxxl"])
	comment = TextareaElement(locators["ticket.member.comment"])

	rep_firstname = TextfieldElement(locators["ticket.member.rep.firstname"])
	rep_lastname = TextfieldElement(locators["ticket.member.rep.lastname"])
	rep_email = TextfieldElement(locators["ticket.member.rep.email"])
	rep_street = TextfieldElement(locators["ticket.member.rep.street"])
	rep_zip = TextfieldElement(locators["ticket.member.rep.zip"])
	rep_city = TextfieldElement(locators["ticket.member.rep.city"])
	rep_country = TextfieldElement(locators["ticket.member.rep.country"])
	rep_type = RadiobuttonElement(locators["ticket.member.rep.type"])

	tshirt_type = RadiobuttonElement(locators["ticket.member.tshirt.type"])
	tshirt_size = RadiobuttonElement(locators["ticket.member.tshirt.size"])

	submit = ButtonElement(locators["ticket.member.ticket.submit"])
	reedit = ButtonElement(locators["ticket.member.confirm.reedit"])
	confirm = ButtonElement(locators["ticket.member.confirm.confirm"])

	def __init__(self, cfg):
		self.cfg = cfg
		client.cli.get(server.srv.url+server.srv.lu)
		#self.assertEqual(client.cli.current_url, server.srv.url)