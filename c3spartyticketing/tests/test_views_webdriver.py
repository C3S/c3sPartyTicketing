# _*_ coding: utf-8 _*_
import os
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from cfg import cfg
from pageobject import (
	server,
	client
)
import re
from datetime import (
	date,
	datetime,
	timedelta
)
from pageobject.ticket_member import TicketMemberObject
from pageobject.ticket_nonmember import TicketNonmemberObject

from c3spartyticketing.models import PartyTicket
import transaction

import string
import random

import coverage

# clear screen once for all selenium tests
folder = cfg['dbg']['screenshotPath']
png = re.compile('^.*\.png$')
for f in os.listdir(folder):
	file_path = os.path.join(folder, f)
	try:
		if os.path.isfile(file_path) and png.match(f):
			os.unlink(file_path)
	except Exception, e:
		print e

# XXX: put class in webutils
class SeleniumTestBase(unittest.TestCase):

	# overload: configuration of individual appSettings
	@classmethod
	def appSettings(cls):
		return {}

	@classmethod
	def setUpClass(cls):
		cls.cfg = cfg
		cls.srv = server.connect(
			cfg=cls.cfg, 
			customAppSettings=cls.appSettings(), 
            wrapper='StopableWSGIServer'
        )
		cls.cli = client.connect(
			cfg=cls.cfg
		)

	@classmethod
	def tearDownClass(cls):
		client.disconnect()
		server.disconnect()

	def screen(self, name=''):
		if self.cfg['dbg']['screenshot']:
			self.cli.get_screenshot_as_file(
				self.cfg['dbg']['screenshotPath'] + self.__class__.__name__ 
				+ "-" + self._testMethodName + '-' + name + '.png'
			)

	def logSection(self, name=''):
		if self.cfg['dbg']['logSection']:
			line = '~'*80
			testclass = self.__class__.__name__
			testname = self._testMethodName
			print(
				"\n\n" + line
				+"\n   " + testclass + "." + testname + ": " + name
				+"\n\n" + line
			)

	def checkErrorPage(self):
		# error traceback of pserve
		self.assertFalse(
			'<strong class="arthur">DONT PANIC</strong>' in self.cli.page_source
		)


class SeleniumTestBaseTicketing(SeleniumTestBase):

	@classmethod
	def appSettings(cls):
		today = datetime.today().date()
		yesterday = (datetime.today() - timedelta(1)).date()
		return {
			'registration.finish_on_submit': 'true',
			'registration.end': str(today),
			'registration.endgvonly': str(today),
		}

	# get target class
	def _getTargetClass(self):
		from c3spartyticketing.models import PartyTicket
		return PartyTicket

	# make a random string
	def _rnd(self, size=6, chars=string.ascii_uppercase + string.digits):
		return u''.join(random.choice(chars) for _ in range(size))

	# make a random instance of target class
	def _makeRandom(self,
					token=None,
					firstname=None,
					lastname=None,
					email=None,
					password=None,
					locale=u"de",
					email_is_confirmed=False,
					email_confirm_code=False,
					date_of_submission=date.today(),
					num_tickets=1,
					ticket_gv_attendance=0,
					ticket_bc_attendance=False,
					ticket_bc_buffet=False,
					ticket_tshirt=False,
					ticket_tshirt_type=None,
					ticket_tshirt_size=None,
					ticket_all=False,
					ticket_support=False,
					ticket_support_x=False,
					ticket_support_xl=False,
					support=0,
					discount=0,
					the_total=0,
					rep_firstname=None,
					rep_lastname=None,
					rep_street=None,
					rep_zip=None,
					rep_city=None,
					rep_country=None,
					rep_type='member',
					guestlist=False,
					user_comment=None,
					membership_type=u'normal'
					):
		_ticket = self._getTargetClass()(  # order of params DOES matter
			token or self._rnd(),
			firstname or self._rnd(),
			lastname or self._rnd(),
			email or self._rnd()+'@test.c3s.cc',
			password or self._rnd(),
			locale,
			email_is_confirmed,
			email_confirm_code or self._rnd(),
			date_of_submission,
			num_tickets,
			ticket_gv_attendance,
			ticket_bc_attendance,
			ticket_bc_buffet,
			ticket_tshirt,
			ticket_tshirt_type,
			ticket_tshirt_size,
			ticket_all,
			ticket_support,
			ticket_support_x,
			ticket_support_xl,
			support,
			discount,
			the_total,
			rep_firstname or self._rnd(),
			rep_lastname or self._rnd(),
			rep_street or self._rnd(),
			rep_zip or self._rnd(),
			rep_city or self._rnd(),
			rep_country or self._rnd(),
			rep_type,
			guestlist,
			user_comment or self._rnd()
		)
		_ticket.membership_type = membership_type
		return _ticket

# XXX: test validation errors
# XXX: test form logic: check manipulation correction after submit
# XXX: test python form logic: calculated values (total, ...)
# XXX: test cases of user feedback
# XXX: test changes of route inbetween member/nonmember

### Member #####################################################################

class TicketMemberFormAccessTests(SeleniumTestBaseTicketing):
	"""
	tests access to the ticket form for members
	"""

	def setUp(self):
		self.logSection()
		# delete member ticket in db if present
		with transaction.manager:
			PartyTicket.delete_by_token(self.cfg['member']['token'])
		# renew session for each single test
		self.cli.delete_all_cookies()

	def test_access_without_token(self):
		# route: root
		self.cli.get(self.srv.url);
		self.screen('ticket')
		self.assertTrue(
			self.cli.current_url.endswith(
				server.appSettings['registration.access_denied_url']
			)
		)
		self.checkErrorPage()
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertTrue(
			self.cli.current_url.endswith(
				server.appSettings['registration.access_denied_url']
			)
		)
		self.checkErrorPage()
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertTrue(
			self.cli.current_url.endswith(
				server.appSettings['registration.access_denied_url']
			)
		)
		self.checkErrorPage()
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertTrue(
			self.cli.current_url.endswith(
				server.appSettings['registration.access_denied_url']
			)
		)
		self.checkErrorPage()

	def test_access_with_token_not_in_db(self):
		# load user
		self.cli.get(self.srv.url+self.srv.lu)
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url)
		self.checkErrorPage()

	def test_access_with_token_in_db(self):
		with transaction.manager:
			ticket = self._makeRandom(
				firstname=self.cfg['member']['firstname'],
				lastname=self.cfg['member']['lastname'],
				email=self.cfg['member']['email'],
				token=self.cfg['member']['token']
			)
			self.srv.db.add(ticket)
		# load user
		self.cli.get(self.srv.url+self.srv.lu)
		self.screen('lu')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: ticket
		self.cli.get(self.srv.url);
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()


class TicketMemberFormFieldValuesTests(SeleniumTestBaseTicketing):
	"""
	tests the ticket form for members using selenium
	covers also package pageobject
	"""

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)
		# data provider
		self.data_checkbox = [False, False, True, True, False, True, False]
		self.data_generalassembly = ["1", "2", "3"]
		self.data_rep_type = ["member", "partner", "parent", "child", "sibling"]
		self.data_tshirt_type = ["m", "f"]
		self.data_tshirt_size = ["S", "M", "L", "XL", "XXL", "XXXL"]

	def test_hidden_values(self):
		f = self.form
		self.assertEqual(f.firstname.get(), self.cfg['member']['firstname'])
		self.assertEqual(f.lastname.get(), self.cfg['member']['lastname'])
		self.assertEqual(f.token.get(), self.cfg['member']['token'])

	def test_generalassembly_values(self):
		f = self.form
		for i in self.data_generalassembly:
			f.generalassembly.set(i)
			self.assertEqual(f.generalassembly.get(), i)

	def test_barcamp_values(self):
		f = self.form
		for i in self.data_checkbox:
			f.barcamp.set(i)
			self.assertEqual(f.barcamp.get(), i)

	def test_buffet_values(self):
		f = self.form
		f.barcamp.set(True)
		for i in self.data_checkbox:
			f.buffet.set(i)
			self.assertEqual(f.buffet.get(), i)

	def test_tshirt_values(self):
		f = self.form
		for i in self.data_checkbox:
			f.tshirt.set(i)
			self.assertEqual(f.tshirt.get(), i)

	def test_support_values(self):
		f = self.form
		for i in self.data_checkbox:
			f.support.set(i)
			self.assertEqual(f.support.get(), i)

	def test_supportxl_values(self):
		f = self.form
		for i in self.data_checkbox:
			f.supportxl.set(i)
			self.assertEqual(f.supportxl.get(), i)

	def test_supportxxl_values(self):
		f = self.form
		for i in self.data_checkbox:
			f.supportxxl.set(i)
			self.assertEqual(f.supportxxl.get(), i)

	def test_comment_values(self):
		f = self.form
		f.comment.set("test")
		self.assertEqual(f.comment.get(), "test")

	def test_rep_firstname_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_firstname.set("firstname")
		self.assertEqual(f.rep_firstname.get(), "firstname")

	def test_rep_lastname_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_lastname.set("lastname")
		self.assertEqual(f.rep_lastname.get(), "lastname")

	def test_rep_email_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_email.set("email")
		self.assertEqual(f.rep_email.get(), "email")

	def test_rep_street_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_street.set("street")
		self.assertEqual(f.rep_street.get(), "street")

	def test_rep_zip_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_zip.set("zip")
		self.assertEqual(f.rep_zip.get(), "zip")

	def test_rep_city_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_city.set("city")
		self.assertEqual(f.rep_city.get(), "city")

	def test_rep_country_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_country.set("country")
		self.assertEqual(f.rep_country.get(), "country")

	def test_rep_type_values(self):
		f = self.form
		f.generalassembly.set("2")
		for i in self.data_rep_type:
			f.rep_type.set(i)
			self.assertEqual(f.rep_type.get(), i)

	def test_tshirt_type_values(self):
		f = self.form
		f.tshirt.set(True)
		for i in self.data_tshirt_type:
			f.tshirt_type.set(i)
			self.assertEqual(f.tshirt_type.get(), i)

	def test_tshirt_size_values(self):
		f = self.form
		f.tshirt.set(True)
		for i in self.data_tshirt_size:
			f.tshirt_size.set(i)
			self.assertEqual(f.tshirt_size.get(), i)


class TicketMemberFormFieldLogicTests(SeleniumTestBaseTicketing):

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)

	def test_buffet_logic(self):
		f = self.form
		f.barcamp.set(False)
		self.assertEqual(f.buffet().is_enabled(), False)
		f.barcamp.set(True)
		self.assertEqual(f.buffet().is_enabled(), True)

	def test_allinc_logic(self):
		f = self.form
		# activation
		f.allinc.set(True)
		self.assertEqual(f.allinc.get(), True)
		self.assertEqual(f.allinc().is_enabled(), False)
		self.assertEqual(f.generalassembly.get(), "1")
		self.assertEqual(f.barcamp.get(), True)
		self.assertEqual(f.buffet.get(), True)
		self.assertEqual(f.tshirt.get(), True)
		# deactivation
		f.allinc.set(True)
		f.generalassembly.set("2")
		self.assertEqual(f.allinc.get(), False)
		f.allinc.set(True)
		f.generalassembly.set("3")
		self.assertEqual(f.allinc.get(), False)
		f.allinc.set(True)
		f.barcamp.set(False)
		self.assertEqual(f.allinc.get(), False)
		f.allinc.set(True)
		f.buffet.set(False)
		self.assertEqual(f.allinc.get(), False)
		f.allinc.set(True)
		f.tshirt.set(False)
		self.assertEqual(f.allinc.get(), False)

	def test_tshirt_logic(self):
		f = self.form
		f.tshirt.set(False)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-type").is_displayed(),
			False
		)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-size").is_displayed(),
			False
		)
		f.tshirt.set(True)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-type").is_displayed(),
			True
		)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-size").is_displayed(),
			True
		)

	def test_rep_logic(self):
		f = self.form
		f.generalassembly.set("1")
		self.assertEqual(f.rep_firstname().is_displayed(), False)
		self.assertEqual(f.rep_lastname().is_displayed(), False)
		self.assertEqual(f.rep_email().is_displayed(), False)
		self.assertEqual(f.rep_street().is_displayed(), False)
		self.assertEqual(f.rep_zip().is_displayed(), False)
		self.assertEqual(f.rep_city().is_displayed(), False)
		self.assertEqual(f.rep_country().is_displayed(), False)
		self.assertEqual(
			self.cli.find_element_by_id("item-rep-type").is_displayed(),
			False
		)
		f.generalassembly.set("2")
		self.assertEqual(f.rep_firstname().is_displayed(), True)
		self.assertEqual(f.rep_lastname().is_displayed(), True)
		self.assertEqual(f.rep_email().is_displayed(), True)
		self.assertEqual(f.rep_street().is_displayed(), True)
		self.assertEqual(f.rep_zip().is_displayed(), True)
		self.assertEqual(f.rep_city().is_displayed(), True)
		self.assertEqual(f.rep_country().is_displayed(), True)
		self.assertEqual(
			self.cli.find_element_by_id("item-rep-type").is_displayed(),
			True
		)


class TicketMemberFormActionRedirectsTests(SeleniumTestBaseTicketing):

	def setUp(self):
		self.logSection()
		# delete member ticket in db if present
		with transaction.manager:
			PartyTicket.delete_by_token(self.cfg['member']['token'])
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)

	def test_ticket_submit_redirect(self):
		f = self.form
		# enter arbitrary valid data
		f.generalassembly.set("3")
		self.screen("before")
		f.submit()
		self.screen("after")
		# check url
		self.assertEqual(
			self.cli.current_url,
			self.srv.url+"confirm"
		)

	def test_confirm_reedit_redirect(self):
		f = self.form
		# enter arbitrary valid data
		f.generalassembly.set("3")
		f.submit()
		self.screen("before")
		f.reedit()
		self.screen("after")
		# check url
		self.assertEqual(
			self.cli.current_url,
			self.srv.url+"?reedit"
		)

	def test_confirm_submit_redirect(self):
		f = self.form
		# enter arbitrary valid data
		f.generalassembly.set("3")
		f.submit()
		self.screen("before")
		f.confirm()
		self.screen("after")
		# check url
		self.assertEqual(
			self.cli.current_url,
			self.srv.url+"success"
		)


class TicketMemberFormActionDataTests(SeleniumTestBaseTicketing):

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)

	def test_ticket_submit_data(self):
		f = self.form
		# fill all fields with valid data
		f.generalassembly.set("2")
		f.barcamp.set(True)
		f.buffet.set(True)
		f.tshirt.set(True)
		f.support.set(True)
		f.supportxl.set(True)
		f.supportxxl.set(True)
		f.comment.set("comment")
		f.rep_firstname.set("rep_firstname")
		f.rep_lastname.set("rep_lastname")
		f.rep_email.set("rep@c3s.cc")
		f.rep_street.set("rep_street")
		f.rep_zip.set("rep_zip")
		f.rep_city.set("rep_city")
		f.rep_country.set("rep_country")
		f.rep_type.set("sibling")
		f.tshirt_type.set("f")
		f.tshirt_size.set("L")
		self.screen("before")
		f.submit()
		self.screen("after")
		# check data
		self.assertEqual(f.firstname.getRo(), self.cfg['member']['firstname'])
		self.assertEqual(f.lastname.getRo(), self.cfg['member']['lastname'])
		self.assertEqual(f.email.getRo(), self.cfg['member']['email'])
		self.assertEqual(f.generalassembly.getRo(), "1")
		self.assertEqual(f.barcamp.getRo(), True)
		self.assertEqual(f.buffet.getRo(), True)
		self.assertEqual(f.tshirt.getRo(), True)
		self.assertEqual(f.support.getRo(), True)
		self.assertEqual(f.supportxl.getRo(), True)
		self.assertEqual(f.supportxxl.getRo(), True)
		self.assertEqual(f.comment.getRo(), "comment")
		self.assertEqual(f.rep_firstname.getRo(), "rep_firstname")
		self.assertEqual(f.rep_lastname.getRo(), "rep_lastname")
		self.assertEqual(f.rep_email.getRo(), "rep@c3s.cc")
		self.assertEqual(f.rep_street.getRo(), "rep_street")
		self.assertEqual(f.rep_zip.getRo(), "rep_zip")
		self.assertEqual(f.rep_city.getRo(), "rep_city")
		self.assertEqual(f.rep_country.getRo(), "rep_country")
		self.assertEqual(f.rep_type.getRo(), "4")
		self.assertEqual(f.tshirt_type.getRo(), "1")
		self.assertEqual(f.tshirt_size.getRo(), "2")

	def test_confirm_reedit_data(self):
		f = self.form
		# fill all fields with valid data
		f.generalassembly.set("2")
		f.barcamp.set(True)
		f.buffet.set(True)
		f.tshirt.set(True)
		f.support.set(True)
		f.supportxl.set(True)
		f.supportxxl.set(True)
		f.comment.set("comment")
		f.rep_firstname.set("rep_firstname")
		f.rep_lastname.set("rep_lastname")
		f.rep_email.set("rep@c3s.cc")
		f.rep_street.set("rep_street")
		f.rep_zip.set("rep_zip")
		f.rep_city.set("rep_city")
		f.rep_country.set("rep_country")
		f.rep_type.set("sibling")
		f.tshirt_type.set("f")
		f.tshirt_size.set("L")
		f.submit()
		f.reedit()
		# reedit and check rep fields
		f.rep_firstname.set("rep_firstname-reedit")
		f.rep_lastname.set("rep_lastname-reedit")
		f.rep_email.set("rep-reedit@c3s.cc")
		f.rep_street.set("rep_street-reedit")
		f.rep_zip.set("rep_zip-reedit")
		f.rep_city.set("rep_city-reedit")
		f.rep_country.set("rep_country-reedit")
		f.rep_type.set("member")
		self.screen("rep-before")
		f.submit()
		self.screen("rep-after")
		self.assertEqual(f.rep_firstname.getRo(), "rep_firstname-reedit")
		self.assertEqual(f.rep_lastname.getRo(), "rep_lastname-reedit")
		self.assertEqual(f.rep_email.getRo(), "rep-reedit@c3s.cc")
		self.assertEqual(f.rep_street.getRo(), "rep_street-reedit")
		self.assertEqual(f.rep_zip.getRo(), "rep_zip-reedit")
		self.assertEqual(f.rep_city.getRo(), "rep_city-reedit")
		self.assertEqual(f.rep_country.getRo(), "rep_country-reedit")
		self.assertEqual(f.rep_type.getRo(), "0")
		# reedit and check tshirt fields
		f.reedit()
		f.tshirt_type.set("m")
		f.tshirt_size.set("S")
		self.screen("tshirt-before")
		f.submit()
		self.screen("tshirt-after")
		self.assertEqual(f.tshirt_type.getRo(), "0")
		self.assertEqual(f.tshirt_size.getRo(), "0")
		# reedit and check ticket fields
		f.reedit()
		f.generalassembly.set("3")
		f.buffet.set(False)
		f.barcamp.set(False)
		f.tshirt.set(False)
		f.support.set(False)
		f.supportxl.set(False)
		f.supportxxl.set(False)
		f.comment.set("comment-reedit")
		self.screen("ticket-before")
		f.submit()
		self.screen("ticket-after")
		self.assertEqual(f.generalassembly.getRo(), "2")
		self.assertEqual(f.barcamp.getRo(), False)
		self.assertEqual(f.buffet.getRo(), False)
		self.assertEqual(f.tshirt.getRo(), False)
		self.assertEqual(f.support.getRo(), False)
		self.assertEqual(f.supportxl.getRo(), False)
		self.assertEqual(f.supportxxl.getRo(), False)
		self.assertEqual(f.comment.getRo(), "comment-reedit")
		

class TicketMemberCasesUserfeedbackTests(SeleniumTestBaseTicketing):

	def setUp(self):
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(cfg)

	def test_gv_transaction(self):
		self.skipTest('2DO')
		self.logSection()
		f = self.form

	def test_gv_notransaction(self):
		self.skipTest('2DO')
		self.logSection()
		f = self.form
		pass

	def test_notgv_bc(self):
		self.skipTest('2DO')
		self.logSection()
		f = self.form
		pass

	def test_notgv_notbc_transaction(self):
		self.skipTest('2DO')
		self.logSection()
		f = self.form
		pass
	
	def test_notgv_notbc_notransaction(self):
		self.skipTest('2DO')
		self.logSection()
		f = self.form
		pass


class TicketMemberFormGvonlyAccessTests(SeleniumTestBaseTicketing):
	"""
	tests access to the ticket form for members
	"""

	@classmethod
	def appSettings(cls):
		today = datetime.today().date()
		yesterday = (datetime.today() - timedelta(1)).date()
		return {
			'registration.finish_on_submit': 'true',
			'registration.end': str(yesterday),
			'registration.endgvonly': str(today),
		}

	def setUp(self):
		self.logSection()
		# init form
		self.form = TicketMemberObject(self.cfg)
		# renew session for each single test
		self.cli.delete_all_cookies()

	def test_access_without_token(self):
		# route: root
		self.cli.get(self.srv.url);
		self.screen('ticket')
		self.assertTrue(
			self.cli.current_url.endswith('/barcamp/end')
		)
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertTrue(
			self.cli.current_url.endswith('/barcamp/end')
		)
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertTrue(
			self.cli.current_url.endswith('/barcamp/end')
		)
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertTrue(
			self.cli.current_url.endswith('/barcamp/end')
		)

	def test_access_with_token(self):
		f = self.form
		# load user
		self.cli.get(self.srv.url+self.srv.lu)
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url)
		# check, if form is gvonly
		with self.assertRaises(NoSuchElementException):
			f.barcamp()
		with self.assertRaises(NoSuchElementException):
			f.buffet()
		with self.assertRaises(NoSuchElementException):
			f.tshirt()
		with self.assertRaises(NoSuchElementException):
			f.allinc()
		with self.assertRaises(NoSuchElementException):
			f.support()
		with self.assertRaises(NoSuchElementException):
			f.supportxl()
		with self.assertRaises(NoSuchElementException):
			f.supportxxl()
		with self.assertRaises(NoSuchElementException):
			f.tshirt_type()
		with self.assertRaises(NoSuchElementException):
			f.tshirt_size()


class TicketMemberFormGvonlyFieldValuesTests(SeleniumTestBaseTicketing):
	"""
	tests the ticket form gvonly for members using selenium
	covers also package pageobject
	"""

	@classmethod
	def appSettings(cls):
		today = datetime.today().date()
		yesterday = (datetime.today() - timedelta(1)).date()
		return {
			'registration.finish_on_submit': 'true',
			'registration.end': str(yesterday),
			'registration.endgvonly': str(today),
		}

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)
		# data provider
		self.data_checkbox = [False, False, True, True, False, True, False]
		self.data_generalassembly = ["1", "2", "3"]
		self.data_rep_type = ["member", "partner", "parent", "child", "sibling"]

	def test_hidden_values(self):
		f = self.form
		self.assertEqual(f.firstname.get(), self.cfg['member']['firstname'])
		self.assertEqual(f.lastname.get(), self.cfg['member']['lastname'])
		self.assertEqual(f.token.get(), self.cfg['member']['token'])

	def test_generalassembly_values(self):
		f = self.form
		for i in self.data_generalassembly:
			f.generalassembly.set(i)
			self.assertEqual(f.generalassembly.get(), i)

	def test_comment_values(self):
		f = self.form
		f.comment.set("test")
		self.assertEqual(f.comment.get(), "test")

	def test_rep_firstname_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_firstname.set("firstname")
		self.assertEqual(f.rep_firstname.get(), "firstname")

	def test_rep_lastname_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_lastname.set("lastname")
		self.assertEqual(f.rep_lastname.get(), "lastname")

	def test_rep_email_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_email.set("email")
		self.assertEqual(f.rep_email.get(), "email")

	def test_rep_street_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_street.set("street")
		self.assertEqual(f.rep_street.get(), "street")

	def test_rep_zip_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_zip.set("zip")
		self.assertEqual(f.rep_zip.get(), "zip")

	def test_rep_city_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_city.set("city")
		self.assertEqual(f.rep_city.get(), "city")

	def test_rep_country_values(self):
		f = self.form
		f.generalassembly.set("2")
		f.rep_country.set("country")
		self.assertEqual(f.rep_country.get(), "country")

	def test_rep_type_values(self):
		f = self.form
		f.generalassembly.set("2")
		for i in self.data_rep_type:
			f.rep_type.set(i)
			self.assertEqual(f.rep_type.get(), i)


class TicketMemberFormGvonlyActionDataTests(SeleniumTestBaseTicketing):
	"""
	tests route, if registation is gvonly
	"""

	@classmethod
	def appSettings(cls):
		today = datetime.today().date()
		yesterday = (datetime.today() - timedelta(1)).date()
		return {
			'registration.finish_on_submit': 'true',
			'registration.end': str(yesterday),
			'registration.endgvonly': str(today),
		}

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)

	def test_ticket_submit_data(self):
		f = self.form
		# fill all fields with valid data
		f.generalassembly.set("2")
		f.comment.set("comment")
		f.rep_firstname.set("rep_firstname")
		f.rep_lastname.set("rep_lastname")
		f.rep_email.set("rep@c3s.cc")
		f.rep_street.set("rep_street")
		f.rep_zip.set("rep_zip")
		f.rep_city.set("rep_city")
		f.rep_country.set("rep_country")
		f.rep_type.set("sibling")
		self.screen("before")
		f.submit()
		self.screen("after")
		# check data
		self.assertEqual(f.firstname.getRo(), self.cfg['member']['firstname'])
		self.assertEqual(f.lastname.getRo(), self.cfg['member']['lastname'])
		self.assertEqual(f.email.getRo(), self.cfg['member']['email'])
		self.assertEqual(f.generalassembly.getRo(), "1")
		self.assertEqual(f.comment.getRo(), "comment")
		self.assertEqual(f.rep_firstname.getRo(), "rep_firstname")
		self.assertEqual(f.rep_lastname.getRo(), "rep_lastname")
		self.assertEqual(f.rep_email.getRo(), "rep@c3s.cc")
		self.assertEqual(f.rep_street.getRo(), "rep_street")
		self.assertEqual(f.rep_zip.getRo(), "rep_zip")
		self.assertEqual(f.rep_city.getRo(), "rep_city")
		self.assertEqual(f.rep_country.getRo(), "rep_country")
		self.assertEqual(f.rep_type.getRo(), "4")

	def test_confirm_reedit_data(self):
		f = self.form
		# fill all fields with valid data
		f.generalassembly.set("2")
		f.comment.set("comment")
		f.rep_firstname.set("rep_firstname")
		f.rep_lastname.set("rep_lastname")
		f.rep_email.set("rep@c3s.cc")
		f.rep_street.set("rep_street")
		f.rep_zip.set("rep_zip")
		f.rep_city.set("rep_city")
		f.rep_country.set("rep_country")
		f.rep_type.set("sibling")
		f.submit()
		f.reedit()
		# reedit and check rep fields
		f.rep_firstname.set("rep_firstname-reedit")
		f.rep_lastname.set("rep_lastname-reedit")
		f.rep_email.set("rep-reedit@c3s.cc")
		f.rep_street.set("rep_street-reedit")
		f.rep_zip.set("rep_zip-reedit")
		f.rep_city.set("rep_city-reedit")
		f.rep_country.set("rep_country-reedit")
		f.rep_type.set("member")
		self.screen("rep-before")
		f.submit()
		self.screen("rep-after")
		self.assertEqual(f.rep_firstname.getRo(), "rep_firstname-reedit")
		self.assertEqual(f.rep_lastname.getRo(), "rep_lastname-reedit")
		self.assertEqual(f.rep_email.getRo(), "rep-reedit@c3s.cc")
		self.assertEqual(f.rep_street.getRo(), "rep_street-reedit")
		self.assertEqual(f.rep_zip.getRo(), "rep_zip-reedit")
		self.assertEqual(f.rep_city.getRo(), "rep_city-reedit")
		self.assertEqual(f.rep_country.getRo(), "rep_country-reedit")
		self.assertEqual(f.rep_type.getRo(), "0")
		# reedit and check ticket fields
		f.reedit()
		f.generalassembly.set("3")
		f.comment.set("comment-reedit")
		self.screen("ticket-before")
		f.submit()
		self.screen("ticket-after")
		self.assertEqual(f.generalassembly.getRo(), "2")
		self.assertEqual(f.comment.getRo(), "comment-reedit")


class TicketMemberRegistrationEndTests(SeleniumTestBaseTicketing):
	"""
	tests route, if registation ended
	"""

	@classmethod
	def appSettings(cls):
		today = datetime.today().date()
		yesterday = (datetime.today() - timedelta(1)).date()
		return {
			'registration.finish_on_submit': 'true',
			'registration.end': str(yesterday),
			'registration.endgvonly': str(yesterday),
		}

	def setUp(self):
		self.logSection()
		# delete member ticket in db if present
		with transaction.manager:
			PartyTicket.delete_by_token(self.cfg['member']['token'])
		# renew session for each single test
		self.cli.delete_all_cookies()

	def test_access_with_token_not_in_db(self):
		# load user
		self.cli.get(self.srv.url+self.srv.lu)
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url+"end")
		self.checkErrorPage()
		# route: ticket
		self.cli.get(self.srv.url);
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url+"end")
		self.checkErrorPage()
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertEqual(self.cli.current_url, self.srv.url+"end")
		self.checkErrorPage()
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertEqual(self.cli.current_url, self.srv.url+"end")
		self.checkErrorPage()
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertEqual(self.cli.current_url, self.srv.url+"end")
		self.checkErrorPage()

	def test_access_with_token_in_db(self):
		with transaction.manager:
			ticket = self._makeRandom(
				firstname=self.cfg['member']['firstname'],
				lastname=self.cfg['member']['lastname'],
				email=self.cfg['member']['email'],
				token=self.cfg['member']['token']
			)
			self.srv.db.add(ticket)
		# load user
		self.cli.get(self.srv.url+self.srv.lu)
		self.screen('load')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: ticket
		self.cli.get(self.srv.url);
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertEqual(self.cli.current_url, self.srv.url+"finished")
		self.checkErrorPage()



### Nonmember ##################################################################

class TicketNonmemberFormAccessTests(SeleniumTestBaseTicketing):
	"""
	tests access to the ticket form for nonmembers
	"""

	def setUp(self):
		# renew session for each single test
		self.cli.delete_all_cookies()

	def test_access(self):
		self.logSection()
		# route: nonmember
		self.cli.get(self.srv.url+"barcamp");
		self.screen('ticket')
		self.assertTrue(self.cli.current_url.endswith("/barcamp"))
		self.checkErrorPage()
		# route: nonmember_confirm
		self.cli.get(self.srv.url+'barcamp/confirm')
		self.screen('confirm')
		self.assertTrue(self.cli.current_url.endswith("/barcamp"))
		self.checkErrorPage()
		# route: nonmember_success
		self.cli.get(self.srv.url+'barcamp/success')
		self.screen('success')
		self.assertTrue(self.cli.current_url.endswith("/barcamp"))
		self.checkErrorPage()


class TicketNonemberFormFieldValuesTests(SeleniumTestBaseTicketing):
	"""
	tests the ticket form for nonmembers using selenium
	covers also package pageobject
	"""

	def setUp(self):
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketNonmemberObject(self.cfg)
		# data provider
		self.data_checkbox = [False, False, True, True, False, True, False]
		self.data_tshirt_type = ["m", "f"]
		self.data_tshirt_size = ["S", "M", "L", "XL", "XXL", "XXXL"]

	def test_firstname_values(self):
		self.logSection()
		f = self.form
		f.firstname.set("firstname")
		self.assertEqual(f.firstname.get(), "firstname")

	def test_lastname_values(self):
		self.logSection()
		f = self.form
		f.lastname.set("lastname")
		self.assertEqual(f.lastname.get(), "lastname")

	def test_email_values(self):
		self.logSection()
		f = self.form
		f.email.set("test@c3s.cc")
		self.assertEqual(f.email.get(), "test@c3s.cc")

	def test_barcamp_values(self):
		self.logSection()
		f = self.form
		for i in self.data_checkbox:
			f.barcamp.set(i)
			self.assertEqual(f.barcamp.get(), i)

	def test_buffet_values(self):
		self.logSection()
		f = self.form
		f.barcamp.set(True)
		for i in self.data_checkbox:
			f.buffet.set(i)
			self.assertEqual(f.buffet.get(), i)

	def test_tshirt_values(self):
		self.logSection()
		f = self.form
		for i in self.data_checkbox:
			f.tshirt.set(i)
			self.assertEqual(f.tshirt.get(), i)

	def test_support_values(self):
		self.logSection()
		f = self.form
		for i in self.data_checkbox:
			f.support.set(i)
			self.assertEqual(f.support.get(), i)

	def test_supportxl_values(self):
		self.logSection()
		f = self.form
		for i in self.data_checkbox:
			f.supportxl.set(i)
			self.assertEqual(f.supportxl.get(), i)

	def test_supportxxl_values(self):
		self.logSection()
		f = self.form
		for i in self.data_checkbox:
			f.supportxxl.set(i)
			self.assertEqual(f.supportxxl.get(), i)

	def test_comment_values(self):
		self.logSection()
		f = self.form
		f.comment.set("test")
		self.assertEqual(f.comment.get(), "test")

	def test_tshirt_type_values(self):
		self.logSection()
		f = self.form
		f.tshirt.set(True)
		for i in self.data_tshirt_type:
			f.tshirt_type.set(i)
			self.assertEqual(f.tshirt_type.get(), i)

	def test_tshirt_size_values(self):
		self.logSection()
		f = self.form
		f.tshirt.set(True)
		for i in self.data_tshirt_size:
			f.tshirt_size.set(i)
			self.assertEqual(f.tshirt_size.get(), i)


class TicketNonmemberFormFieldLogicTests(SeleniumTestBaseTicketing):

	def setUp(self):
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketNonmemberObject(self.cfg)

	def test_buffet_logic(self):
		self.logSection()
		f = self.form
		f.barcamp.set(False)
		self.assertEqual(f.buffet().is_enabled(), False)
		f.barcamp.set(True)
		self.assertEqual(f.buffet().is_enabled(), True)

	def test_tshirt_logic(self):
		self.logSection()
		f = self.form
		f.tshirt.set(False)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-type").is_displayed(),
			False
		)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-size").is_displayed(),
			False
		)
		f.tshirt.set(True)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-type").is_displayed(),
			True
		)
		self.assertEqual(
			self.cli.find_element_by_id("item-tshirt-size").is_displayed(),
			True
		)

class TicketNonmemberFormActionRedirectsTests(SeleniumTestBaseTicketing):

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketNonmemberObject(self.cfg)

	def test_ticket_submit_redirect(self):
		f = self.form
		# enter arbitrary valid data
		f.firstname.set("firstname")
		f.lastname.set("lastname")
		f.email.set("test@c3s.cc")
		f.barcamp.set(True)
		self.screen("before")
		f.submit()
		self.screen("after")
		# check url
		self.assertEqual(
			self.cli.current_url,
			self.srv.url+"barcamp/confirm"
		)

	def test_confirm_reedit_redirect(self):
		f = self.form
		# enter arbitrary valid data
		f.firstname.set("firstname")
		f.lastname.set("lastname")
		f.email.set("test@c3s.cc")
		f.barcamp.set(True)
		f.submit()
		self.screen("before")
		f.reedit()
		self.screen("after")
		# check url
		self.assertEqual(
			self.cli.current_url,
			self.srv.url+"barcamp?reedit"
		)

	def test_confirm_submit_redirect(self):
		f = self.form
		# enter arbitrary valid data
		f.firstname.set("firstname")
		f.lastname.set("lastname")
		f.email.set("test@c3s.cc")
		f.barcamp.set(True)
		f.submit()
		self.screen("before")
		f.confirm()
		self.screen("after")
		# check url
		self.assertEqual(
			self.cli.current_url,
			self.srv.url+"barcamp/success"
		)


class TicketMemberFormActionDataTests(SeleniumTestBaseTicketing):

	def setUp(self):
		self.logSection()
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketNonmemberObject(self.cfg)

	def test_ticket_submit_data(self):
		f = self.form
		# fill all fields with valid data
		f.firstname.set("firstname")
		f.lastname.set("lastname")
		f.email.set("test@c3s.cc")
		f.barcamp.set(True)
		f.buffet.set(True)
		f.tshirt.set(True)
		f.support.set(True)
		f.supportxl.set(True)
		f.supportxxl.set(True)
		f.comment.set("comment")
		f.tshirt_type.set("f")
		f.tshirt_size.set("L")
		self.screen("before")
		f.submit()
		self.screen("after")
		# check data
		self.assertEqual(f.firstname.getRo(), "firstname")
		self.assertEqual(f.lastname.getRo(), "lastname")
		self.assertEqual(f.email.getRo(), "test@c3s.cc")
		self.assertEqual(f.barcamp.getRo(), True)
		self.assertEqual(f.buffet.getRo(), True)
		self.assertEqual(f.tshirt.getRo(), True)
		self.assertEqual(f.support.getRo(), True)
		self.assertEqual(f.supportxl.getRo(), True)
		self.assertEqual(f.supportxxl.getRo(), True)
		self.assertEqual(f.comment.getRo(), "comment")
		self.assertEqual(f.tshirt_type.getRo(), "1")
		self.assertEqual(f.tshirt_size.getRo(), "2")

	def test_confirm_reedit_data(self):
		f = self.form
		# fill all fields with valid data
		f.firstname.set("firstname")
		f.lastname.set("lastname")
		f.email.set("test@c3s.cc")
		f.barcamp.set(True)
		f.buffet.set(True)
		f.tshirt.set(True)
		f.support.set(True)
		f.supportxl.set(True)
		f.supportxxl.set(True)
		f.comment.set("comment")
		f.tshirt_type.set("f")
		f.tshirt_size.set("L")
		f.submit()
		# reedit and check tshirt fields
		f.reedit()
		f.tshirt_type.set("m")
		f.tshirt_size.set("S")
		self.screen("tshirt-before")
		f.submit()
		self.screen("tshirt-after")
		self.assertEqual(f.tshirt_type.getRo(), "0")
		self.assertEqual(f.tshirt_size.getRo(), "0")
		# reedit and check ticket fields
		f.reedit()
		f.barcamp.set(True)
		f.buffet.set(False)
		f.tshirt.set(False)
		f.support.set(False)
		f.supportxl.set(False)
		f.supportxxl.set(False)
		f.comment.set("comment-reedit")
		self.screen("ticket-before")
		f.submit()
		self.screen("ticket-after")
		self.assertEqual(f.barcamp.getRo(), True)
		self.assertEqual(f.buffet.getRo(), False)
		self.assertEqual(f.tshirt.getRo(), False)
		self.assertEqual(f.support.getRo(), False)
		self.assertEqual(f.supportxl.getRo(), False)
		self.assertEqual(f.supportxxl.getRo(), False)
		self.assertEqual(f.comment.getRo(), "comment-reedit")


class TicketNonmemberRegistrationEndTests(SeleniumTestBaseTicketing):
	"""
	tests route, if registation ended
	"""

	@classmethod
	def appSettings(cls):
		today = datetime.today().date()
		yesterday = (datetime.today() - timedelta(1)).date()
		return {
			'registration.finish_on_submit': 'true',
			'registration.end': str(yesterday),
			'registration.endgvonly': str(yesterday),
		}

	def setUp(self):
		self.logSection()
		# init form
		self.form = TicketNonmemberObject(self.cfg)
		# renew session for each single test
		self.cli.delete_all_cookies()

	def test_access_with_token_not_in_db(self):
		f = self.form
		# route: ticket
		self.cli.get(self.srv.url);
		self.screen('ticket')
		self.assertEqual(self.cli.current_url, self.srv.url+"barcamp/end")
		self.checkErrorPage()
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertEqual(self.cli.current_url, self.srv.url+"barcamp/end")
		self.checkErrorPage()
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertEqual(self.cli.current_url, self.srv.url+"barcamp/end")
		self.checkErrorPage()
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertEqual(self.cli.current_url, self.srv.url+"barcamp/end")
		self.checkErrorPage()


# maybe check https://pypi.python.org/pypi/z3c.webdriver
#
# class TicketFormTests(unittest.TestCase):
# 	"""
# 	test the ticket form using selenium (make a browser do things)
# 	see
# 	http://docs.seleniumhq.org/docs/03_webdriver.jsp
# 		   #introducing-the-selenium-webdriver-api-by-example
# 	http://selenium-python.readthedocs.org/en/latest/api.html
# 	http://selenium.googlecode.com/svn/trunk/docs/api/py/index.html
# 	"""
# 	def setUp(self):
# 		call(['./env/bin/pserve', 'development.ini', 'start'])
# 		time.sleep(3)
# 		self.driver = webdriver.PhantomJS() # Firefox()

# 	def tearDown(self):
# 		self.driver.quit()
# 		call(['./env/bin/pserve', 'development.ini', 'stop'])

# 	def test_form_without_token(self):
# 		from c3spartyticketing.views import party_view  # trigger coverage
# 		self.driver.get("http://0.0.0.0:6544/?de")
# 		# ..and be redirected to the membership form yes.c3s.cc
# 		self.failUnless(
# 			u'Mitgliedschaftsantrag für die Cultural Commons Collecting Society'
# 			in self.driver.page_source)

# 	def test_form_with_token(self):
# 		from c3spartyticketing.views import party_view  # trigger coverage
# 		self.driver.get(
# 			"http://0.0.0.0:6544/lu/DK74PX4JVQ/alexander.blum@c3s.cc"
# 		)
# 		#self.driver.maximize_window()
# 		#inputElement = self.driver.find_element_by_name("firstname")
# 		#inputElement = self.driver.find_element_by_name("comment")
# 		inputElement.send_keys("ein testkommentar")
# 		#self.driver.find_element_by_name('lastname').send_keys('Scheid')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('email').send_keys('c@c3s.cc')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('password').send_keys('foobar')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('address1').send_keys('addr one')
# 		#time.sleep(0.11)
# 		#self.driver.find_element_by_name('address2').send_keys('addr two')
# 		#time.sleep(0.11)
# 		#self.driver.find_element_by_name('postcode').send_keys('98765')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('city').send_keys('townish')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('country').send_keys('Gro')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('year').send_keys(Keys.CONTROL, "a")
# 		#self.driver.find_element_by_name('year').send_keys('1998')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('month').send_keys(Keys.CONTROL, "a")
# 		#self.driver.find_element_by_name('month').send_keys('12')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('day').send_keys(Keys.CONTROL, "a")
# 		#self.driver.find_element_by_name('day').send_keys('12')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('deformField14').click()
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('other_colsoc').click()  # Yes
# 		#self.driver.find_element_by_id('other_colsoc-1').click()  # No
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_id(
# 		#    'colsoc_name').send_keys('GEMA')
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('got_statute').click()
# 		#time.sleep(0.1)
# 		#self.driver.find_element_by_name('num_shares').send_keys('7')

# 		self.driver.find_element_by_name('submit').click()
# 		#print self.driver.page_source
# 		#self.failUnless('Ja, schick mir die Email.' in self.driver.page_source)
# 		self.failUnless('Abschicken' in self.driver.page_source)

# 		# TODO: check contents of success page XXX
# 		#self.assertTrue('Christoph' in self.driver.page_source)
# 		self.assertTrue(u'Bitte die Angaben bestätigen' in self.driver.page_source)
# 		#self.assertTrue('Scheid' in self.driver.page_source)
# 		#self.assertTrue('Was nun passieren muss: Kontrolliere die Angaben '
# 		#                'unten,' in self.driver.page_source)

# 		# TODO: check case colsoc = no views.py 765-767

# 		# TODO: check save to DB/randomstring: views.py 784-865

# 		# TODO: check re-edit of form: views.py 877-880 XXX
# 		#self.failUnless('Angaben ändern' in self.driver.page_source)
# 		self.driver.find_element_by_name('reedit').click()
# 		# back to the form
# 		time.sleep(0.1)  # wait a little
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'lastname').get_attribute('value'), 'Scheid')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'firstname').get_attribute('value'), 'Christoph')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'email').get_attribute('value'), 'c@c3s.cc')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'password').get_attribute('value'), 'foobar')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'address1').get_attribute('value'), 'addr one')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'address2').get_attribute('value'), 'addr two')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'postcode').get_attribute('value'), '98765')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'city').get_attribute('value'), 'townish')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'country').get_attribute('value'), 'GB')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'year').get_attribute('value'), '1998')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'month').get_attribute('value'), '12')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'day').get_attribute('value'), '12')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'deformField14').get_attribute('value'), 'normal')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'other_colsoc').get_attribute('value'), 'yes')
# 		#self.assertEqual(self.driver.find_element_by_id(
# 		#    'colsoc_name').get_attribute('value'), 'GEMA')
# 		#self.assertEqual(self.driver.find_element_by_name(
# 		#    'num_shares').get_attribute('value'), '17')
# 		# change a detail
# 		self.driver.find_element_by_name('address2').send_keys(' plus')
# 		# ok, all data checked, submit again
# 		self.driver.find_element_by_name('submit').click()

# 		self.assertTrue('Bitte beachten: Es gab Fehler. Bitte Eingaben unten '
# 						'korrigieren.' in self.driver.page_source)

# 		# verify we have to theck this again
# 		self.driver.find_element_by_name('got_statute').click()
# 		self.driver.find_element_by_id('other_colsoc-1').click()  # No colsoc
# 		self.driver.find_element_by_name('submit').click()
# 		time.sleep(0.1)
# 		self.assertTrue(
# 			'Bitte beachten: Es gab fehler' not in self.driver.page_source)
# 		self.assertTrue('addr two plus' in self.driver.page_source)

# 		self.driver.find_element_by_name('send_email').click()
# 		time.sleep(0.1)
# 		#import pdb
# 		#pdb.set_trace()

# 		page = self.driver.page_source
# 		self.assertTrue('C3S Mitgliedsantrag: Bitte Emails abrufen.' in page)
# 		self.assertTrue('Eine Email wurde verschickt,' in page)
# 		self.assertTrue('Christoph Scheid!' in page)

# 		self.assertTrue(
# 			u'Du wirst eine Email von noreply@c3s.cc mit einem ' in page)
# 		self.assertTrue(
# 			u'Bestätigungslink erhalten. Bitte rufe Deine Emails ab.' in page)

# 		self.assertTrue(u'Der Betreff der Email lautet:' in page)
# 		self.assertTrue(u'C3S: Email-Adresse' in page)
# 		#self.assertTrue(u'tigen und Formular abrufen.' in page)


# class EmailVerificationTests(unittest.TestCase):

# 	def setUp(self):
# 		call(['./env/bin/pserve', 'development.ini', 'start'])
# 		time.sleep(5)
# 		self.driver = webdriver.PhantomJS() # Firefox()

# 	def tearDown(self):
# 		self.driver.quit()
# 		call(['./env/bin/pserve', 'development.ini', 'stop'])

# 	def test_verify_email(self):  # views.py 296-298
# 		url = "http://0.0.0.0:6543/verify/foo@shri.de/ABCDEFGHIJ"
# 		self.driver.get(url)

# 		self.assertTrue(
# 			'Bitte das Passwort eingeben.' in self.driver.page_source)
# 		self.assertTrue(
# 			'Hier geht es zum PDF...' in self.driver.page_source)
# 		self.driver.find_element_by_name(
# 			'password').send_keys('')  # empty password
# 		self.driver.find_element_by_name('submit').click()

# 		self.assertTrue(
# 			'Bitte das Passwort eingeben.' in self.driver.page_source)
# 		self.assertTrue('Hier geht es zum PDF...' in self.driver.page_source)
# 		self.driver.find_element_by_name(
# 			'password').send_keys('schmoo')  # wrong password
# 		self.driver.find_element_by_name('submit').click()

# 		self.assertTrue(
# 			'Bitte das Passwort eingeben.' in self.driver.page_source)
# 		self.assertTrue('Hier geht es zum PDF...' in self.driver.page_source)
# 		self.driver.find_element_by_name('password').send_keys('berries')
# 		self.driver.find_element_by_name('submit').click()

# 		self.assertTrue('Lade dein PDF...' in self.driver.page_source)
# 		self.assertTrue(
# 			'C3S_SCE_AFM_Firstn_meLastname.pdf' in self.driver.page_source)

#        import pdb
#        pdb.set_trace()


#    def test_verify_email_wrong_pass(self):  # views.py 296-298
#        pass

#    def test_foo(self):
#        pass