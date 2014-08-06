from pageobject import locators, client, server
from pageobject.basepageobject import BasePageObject
from pageobject.basepageelement import (
	HiddenElement,
	TextfieldElement,
	TextareaElement,
	CheckboxElement,
	RadiobuttonElement,
)


class TicketNonmemberObject(BasePageObject):

	firstname = TextfieldElement(locators["ticket.nonmember.firstname"])
	lastname = TextfieldElement(locators["ticket.nonmember.lastname"])
	email = TextfieldElement(locators["ticket.nonmember.email"])

	barcamp = CheckboxElement(locators["ticket.nonmember.barcamp"])
	buffet = CheckboxElement(locators["ticket.nonmember.buffet"])
	tshirt = CheckboxElement(locators["ticket.nonmember.tshirt"])
	support = CheckboxElement(locators["ticket.nonmember.support"])
	supportxl = CheckboxElement(locators["ticket.nonmember.supportxl"])
	supportxxl = CheckboxElement(locators["ticket.nonmember.supportxxl"])
	comment = TextareaElement(locators["ticket.nonmember.comment"])

	tshirt_type = RadiobuttonElement(locators["ticket.nonmember.tshirt.type"])
	tshirt_size = RadiobuttonElement(locators["ticket.nonmember.tshirt.size"])

	def __init__(self, cfg):
		self.cfg = cfg
		client.cli.get(server.srv.url+"barcamp")
		self.assertEqual(client.cli.current_url, server.srv.url+"barcamp")

	# def submit(self):
	# 	wait_for =
	# 	"selenium.browserbot.getCurrentWindow().document.getElementById ('LogoutButton')"
	# 	self.se.click(locators["login.submit"])
	# 	self.se.wait_for_condition(wait_for, "30000")