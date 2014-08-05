# _*_ coding: utf-8 _*_
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC

# available since 2.26.0
import time
from subprocess import call
import pageobjects # kristin


from pageobject import (
	server,
	client
)
from pageobject.ticket_member import TicketMemberObject
# from webtest.http import StopableWSGIServer
# from paste.deploy.loadwsgi import appconfig
# from c3spartyticketing.models import (
#     DBSession,
#     Base,
#     PartyTicket,
#     C3sStaff,
#     Group,
# )
# from sqlalchemy import engine_from_config
# import transaction
# from datetime import date
# import os

# maybe check https://pypi.python.org/pypi/z3c.webdriver


class SeleniumTestBase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		# configuration
		cls.cfg = {
			'app': {
				'host': '0.0.0.0',
				'port': '6545',
				'db': 'test_views_webdriver.db',
				'ini': "development.ini",
				'appconfig': {}, # XXX: override ini
			},
			'webdriver': {
				'driver': webdriver.PhantomJS(), # XXX init not here
				'desired_capabilities': {} # XXX: override default
			},
			'member': {
				'token': 'DK74PX4JVQ',
				'firstname': 'TestVorname',
				'lastname': 'TestNachname',
				'email': 'alexander.blum@c3s.cc'
			},
			'dbg': {
				'logSection': False,
				'screenshot': False,
				'screenshotPath': './c3spartyticketing/tests/screenshots/'
			}
		}
		# connect server / client
		cls.srv = server.connect(cls.cfg)
		cls.srv.url = 'http://' + cls.cfg['app']['host'] + ':' \
			+ cls.cfg['app']['port'] + '/'
		cls.srv.lu = 'lu/' + cls.cfg['member']['token'] + '/' \
			+ cls.cfg['member']['email']
		cls.cli = client.connect(cls.cfg)
		

	@classmethod
	def tearDownClass(cls):
		client.disconnect(cls.cfg)
		server.disconnect(cls.cfg)

	def screen(self, name):
		if self.cfg['dbg']['screenshot']:
			self.cli.get_screenshot_as_file(
				self.cfg['dbg']['screenshotPath'] + self._testMethodName + '-'
				+ name + '.png'
			)

	def logSection(self, name=''):
		if self.cfg['dbg']['logSection']:
			print(
				"\n"
				+"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
				+"\n   "+ self._testMethodName + ': ' + name
				+"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
			)


class TicketMemberAccessTests(SeleniumTestBase):
	"""
	tests access to the ticket form for members
	"""

	def setUp(self):
		# renew session for each single test
		self.cli.delete_all_cookies()

	def test_access_without_token(self):
		self.logSection()
		# route: root
		self.cli.get(self.srv.url);
		self.screen('root')
		self.assertEqual(
			self.cli.current_url, 
			server.appSettings['registration.access_denied_url']
		)
		# route: confirm
		self.cli.get(self.srv.url+'confirm')
		self.screen('confirm')
		self.assertEqual(
			self.cli.current_url, 
			server.appSettings['registration.access_denied_url']
		)
		# route: success
		self.cli.get(self.srv.url+'success')
		self.screen('success')
		self.assertEqual(
			self.cli.current_url, 
			server.appSettings['registration.access_denied_url']
		)
		# route: finished
		self.cli.get(self.srv.url+'finished')
		self.screen('finished')
		self.assertEqual(
			self.cli.current_url, 
			server.appSettings['registration.access_denied_url']
		)

	def test_access_with_token(self):
		self.logSection()
		# load user
		self.cli.get(self.srv.url+self.srv.lu)
		self.screen('lu')
		self.assertEqual(self.cli.current_url, self.srv.url)


class TicketMemberFormFieldValuesTests(SeleniumTestBase):
	"""
	tests the ticket form for members using selenium
	covers also package pageobject
	"""

	def setUp(self):
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
		self.logSection()
		f = self.form
		self.assertEqual(f.firstname.get(), self.cfg['member']['firstname'])
		self.assertEqual(f.lastname.get(), self.cfg['member']['lastname'])
		self.assertEqual(f.token.get(), self.cfg['member']['token'])

	def test_generalassembly_values(self):
		self.logSection()
		f = self.form
		for i in self.data_generalassembly:
			f.generalassembly.set(i)
			self.assertEqual(f.generalassembly.get(), i)

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

	def test_rep_firstname_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_firstname.set("firstname")
		self.assertEqual(f.rep_firstname.get(), "firstname")

	def test_rep_lastname_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_lastname.set("lastname")
		self.assertEqual(f.rep_lastname.get(), "lastname")

	def test_rep_email_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_email.set("email")
		self.assertEqual(f.rep_email.get(), "email")

	def test_rep_street_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_street.set("street")
		self.assertEqual(f.rep_street.get(), "street")

	def test_rep_zip_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_zip.set("zip")
		self.assertEqual(f.rep_zip.get(), "zip")

	def test_rep_city_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_city.set("city")
		self.assertEqual(f.rep_city.get(), "city")

	def test_rep_country_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		f.rep_country.set("country")
		self.assertEqual(f.rep_country.get(), "country")

	def test_rep_type_values(self):
		self.logSection()
		f = self.form
		f.generalassembly.set("2")
		for i in self.data_rep_type:
			f.rep_type.set(i)
			self.assertEqual(f.rep_type.get(), i)

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


class TicketMemberFormFieldLogicTests(SeleniumTestBase):

	def setUp(self):
		# renew session for each single test
		self.cli.delete_all_cookies()
		# init form
		self.form = TicketMemberObject(self.cfg)

	def test_buffet_logic(self):
		self.logSection()
		f = self.form
		f.barcamp.set(False)
		self.assertEqual(f.buffet().is_enabled(), False)
		f.barcamp.set(True)
		self.assertEqual(f.buffet().is_enabled(), True)

	def test_allinc_logic(self):
		self.logSection()
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

	def test_rep_logic(self):
		self.logSection()
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


# XXX: test validation errors
# XXX: test form logic: check manipulation correction after submit
# XXX: test python form logic: calculated values (total, ...)


class TicketFormTests(unittest.TestCase):
	"""
	test the ticket form using selenium (make a browser do things)
	see
	http://docs.seleniumhq.org/docs/03_webdriver.jsp
		   #introducing-the-selenium-webdriver-api-by-example
	http://selenium-python.readthedocs.org/en/latest/api.html
	http://selenium.googlecode.com/svn/trunk/docs/api/py/index.html
	"""
	def setUp(self):
		call(['./env/bin/pserve', 'development.ini', 'start'])
		time.sleep(3)
		self.driver = webdriver.PhantomJS() # Firefox()

	def tearDown(self):
		self.driver.quit()
		call(['./env/bin/pserve', 'development.ini', 'stop'])

	# def test_form_without_token(self):
	# 	from c3spartyticketing.views import party_view  # trigger coverage
	# 	self.driver.get("http://0.0.0.0:6544/?de")
	# 	# ..and be redirected to the membership form yes.c3s.cc
	# 	self.failUnless(
	# 		u'Mitgliedschaftsantrag für die Cultural Commons Collecting Society'
	# 		in self.driver.page_source)

	# def test_form_with_token(self):
	# 	from c3spartyticketing.views import party_view  # trigger coverage
	# 	self.driver.get(
	# 		"http://0.0.0.0:6544/lu/DK74PX4JVQ/alexander.blum@c3s.cc"
	# 	)
	# 	#self.driver.maximize_window()
	# 	#inputElement = self.driver.find_element_by_name("firstname")
	# 	#inputElement = self.driver.find_element_by_name("comment")
	# 	inputElement.send_keys("ein testkommentar")
	# 	#self.driver.find_element_by_name('lastname').send_keys('Scheid')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('email').send_keys('c@c3s.cc')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('password').send_keys('foobar')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('address1').send_keys('addr one')
	# 	#time.sleep(0.11)
	# 	#self.driver.find_element_by_name('address2').send_keys('addr two')
	# 	#time.sleep(0.11)
	# 	#self.driver.find_element_by_name('postcode').send_keys('98765')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('city').send_keys('townish')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('country').send_keys('Gro')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('year').send_keys(Keys.CONTROL, "a")
	# 	#self.driver.find_element_by_name('year').send_keys('1998')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('month').send_keys(Keys.CONTROL, "a")
	# 	#self.driver.find_element_by_name('month').send_keys('12')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('day').send_keys(Keys.CONTROL, "a")
	# 	#self.driver.find_element_by_name('day').send_keys('12')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('deformField14').click()
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('other_colsoc').click()  # Yes
	# 	#self.driver.find_element_by_id('other_colsoc-1').click()  # No
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_id(
	# 	#    'colsoc_name').send_keys('GEMA')
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('got_statute').click()
	# 	#time.sleep(0.1)
	# 	#self.driver.find_element_by_name('num_shares').send_keys('7')

	# 	self.driver.find_element_by_name('submit').click()
	# 	#print self.driver.page_source
	# 	#self.failUnless('Ja, schick mir die Email.' in self.driver.page_source)
	# 	self.failUnless('Abschicken' in self.driver.page_source)

	# 	# TODO: check contents of success page XXX
	# 	#self.assertTrue('Christoph' in self.driver.page_source)
	# 	self.assertTrue(u'Bitte die Angaben bestätigen' in self.driver.page_source)
	# 	#self.assertTrue('Scheid' in self.driver.page_source)
	# 	#self.assertTrue('Was nun passieren muss: Kontrolliere die Angaben '
	# 	#                'unten,' in self.driver.page_source)

	# 	# TODO: check case colsoc = no views.py 765-767

	# 	# TODO: check save to DB/randomstring: views.py 784-865

	# 	# TODO: check re-edit of form: views.py 877-880 XXX
	# 	#self.failUnless('Angaben ändern' in self.driver.page_source)
	# 	self.driver.find_element_by_name('reedit').click()
	# 	# back to the form
	# 	time.sleep(0.1)  # wait a little
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'lastname').get_attribute('value'), 'Scheid')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'firstname').get_attribute('value'), 'Christoph')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'email').get_attribute('value'), 'c@c3s.cc')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'password').get_attribute('value'), 'foobar')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'address1').get_attribute('value'), 'addr one')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'address2').get_attribute('value'), 'addr two')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'postcode').get_attribute('value'), '98765')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'city').get_attribute('value'), 'townish')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'country').get_attribute('value'), 'GB')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'year').get_attribute('value'), '1998')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'month').get_attribute('value'), '12')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'day').get_attribute('value'), '12')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'deformField14').get_attribute('value'), 'normal')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'other_colsoc').get_attribute('value'), 'yes')
	# 	#self.assertEqual(self.driver.find_element_by_id(
	# 	#    'colsoc_name').get_attribute('value'), 'GEMA')
	# 	#self.assertEqual(self.driver.find_element_by_name(
	# 	#    'num_shares').get_attribute('value'), '17')
	# 	# change a detail
	# 	self.driver.find_element_by_name('address2').send_keys(' plus')
	# 	# ok, all data checked, submit again
	# 	self.driver.find_element_by_name('submit').click()

	# 	self.assertTrue('Bitte beachten: Es gab Fehler. Bitte Eingaben unten '
	# 					'korrigieren.' in self.driver.page_source)

	# 	# verify we have to theck this again
	# 	self.driver.find_element_by_name('got_statute').click()
	# 	self.driver.find_element_by_id('other_colsoc-1').click()  # No colsoc
	# 	self.driver.find_element_by_name('submit').click()
	# 	time.sleep(0.1)
	# 	self.assertTrue(
	# 		'Bitte beachten: Es gab fehler' not in self.driver.page_source)
	# 	self.assertTrue('addr two plus' in self.driver.page_source)

	# 	self.driver.find_element_by_name('send_email').click()
	# 	time.sleep(0.1)
	# 	#import pdb
	# 	#pdb.set_trace()

	# 	page = self.driver.page_source
	# 	self.assertTrue('C3S Mitgliedsantrag: Bitte Emails abrufen.' in page)
	# 	self.assertTrue('Eine Email wurde verschickt,' in page)
	# 	self.assertTrue('Christoph Scheid!' in page)

	# 	self.assertTrue(
	# 		u'Du wirst eine Email von noreply@c3s.cc mit einem ' in page)
	# 	self.assertTrue(
	# 		u'Bestätigungslink erhalten. Bitte rufe Deine Emails ab.' in page)

	# 	self.assertTrue(u'Der Betreff der Email lautet:' in page)
	# 	self.assertTrue(u'C3S: Email-Adresse' in page)
	# 	#self.assertTrue(u'tigen und Formular abrufen.' in page)


class EmailVerificationTests(unittest.TestCase):

	def setUp(self):
		call(['./env/bin/pserve', 'development.ini', 'start'])
		time.sleep(5)
		self.driver = webdriver.PhantomJS() # Firefox()

	def tearDown(self):
		self.driver.quit()
		call(['./env/bin/pserve', 'development.ini', 'stop'])

	def test_verify_email(self):  # views.py 296-298
		url = "http://0.0.0.0:6543/verify/foo@shri.de/ABCDEFGHIJ"
		self.driver.get(url)

		self.assertTrue(
			'Bitte das Passwort eingeben.' in self.driver.page_source)
		self.assertTrue(
			'Hier geht es zum PDF...' in self.driver.page_source)
		self.driver.find_element_by_name(
			'password').send_keys('')  # empty password
		self.driver.find_element_by_name('submit').click()

		self.assertTrue(
			'Bitte das Passwort eingeben.' in self.driver.page_source)
		self.assertTrue('Hier geht es zum PDF...' in self.driver.page_source)
		self.driver.find_element_by_name(
			'password').send_keys('schmoo')  # wrong password
		self.driver.find_element_by_name('submit').click()

		self.assertTrue(
			'Bitte das Passwort eingeben.' in self.driver.page_source)
		self.assertTrue('Hier geht es zum PDF...' in self.driver.page_source)
		self.driver.find_element_by_name('password').send_keys('berries')
		self.driver.find_element_by_name('submit').click()

		self.assertTrue('Lade dein PDF...' in self.driver.page_source)
		self.assertTrue(
			'C3S_SCE_AFM_Firstn_meLastname.pdf' in self.driver.page_source)

#        import pdb
#        pdb.set_trace()


#    def test_verify_email_wrong_pass(self):  # views.py 296-298
#        pass

#    def test_foo(self):
#        pass