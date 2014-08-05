# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver
import time
import subprocess
import pageobjects
import os
__author__ = 'Kristin Kuche'


class SeleniumTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.call(['./env/bin/pserve', 'development.ini', 'start'])
        time.sleep(3)

    def setUp(self):
        print "setup"
        pass

    @classmethod
    def tearDownClass(cls):
        subprocess.call(['./env/bin/pserve', 'development.ini', 'stop'])


# class PartyFormTests(SeleniumTestBase):

#     @classmethod
#     def setUpClass(cls):
#         super(PartyFormTests, cls).setUpClass()
#         print "setUp Class -  -  -  -  -"
#         cls.driver = webdriver.PhantomJS() # Firefox()
#         # cls.url_to_test = 'http://0.0.0.0:6544/'
#         cls.url_to_test = 'http://localhost:6544/lu/TR00107035121GP/yes@c3s.cc'
#         cls.driver.get(cls.url_to_test)
#         cls.driver.implicitly_wait(10)  # seconds

#     @classmethod
#     def tearDownClass(cls):
#         super(PartyFormTests, cls).tearDownClass()
#         cls.driver.quit()

#     def setUp(self):
#         super(PartyFormTests, self).setUp()
#         self.driver.get(self.url_to_test)
#         self.page_under_test = pageobjects.PartyPageObject(self.driver)

#     def test_form_with_link(self):
#         url_to_test = 'http://0.0.0.0:6544/lu/TR00107035121GP/yes@c3s.cc'
#         self.driver.get(url_to_test)
#         self.driver.implicitly_wait(2)
#         self.page_under_test.firstname_field.send_keys('Kristin')
#         self.page_under_test = self.page_under_test.submit_form()
#         self.assertEqual(
#            'Kristin',
#            self.page_under_test.firstname_field.get_attribute('value'))
#         print dir(self.driver)

#     def test_submitEmptyForm_errorShown(self):
#         self.page_under_test = self.page_under_test.submit_form()
#         #self.assertIsNotNone(self.driver.find_element_by_id('error-lastname'))
#         #self.assertIsNotNone(
#         #    self.driver.find_element_by_id('error-firstname'))
#         #self.assertIsNotNone(self.driver.find_element_by_id('error-email'))
#         self.assertIsNotNone(
#             self.driver.find_element_by_id('error-attendance-gv'))

#     def test_formIncomplete_errorShown(self):
#         self.page_under_test.firstname = 'Kristin'
#         self.page_under_test.comment = 'Just testing ...'
#         self.page_under_test.ticket_count = 5
#         self.page_under_test.ticket_type = 2
#         self.assertRaises(Exception,
#                           self.driver.find_element_by_id, 'error-lastname')

#         self.page_under_test = self.page_under_test.submit_form()

#         self.assertEqual('Kristin', self.page_under_test.firstname)
#         self.assertEqual('', self.page_under_test.lastname)
#         element = self.driver.find_element_by_id('error-lastname')
#         self.assertIsNotNone(element)
#         self.assertEqual('Just testing ...', self.page_under_test.comment)
#         self.assertEqual(5, self.page_under_test.ticket_count)
#         self.assertEqual(2, self.page_under_test.ticket_type)

#     def test_ticketType1_standardValue1(self):
#         value = self.page_under_test.ticket_type
#         self.assertEqual(1, value)

#     def test_ticketNum_standardValue1(self):
#         value = self.page_under_test.ticket_count
#         self.assertEqual(1, value)

#     def test_ticketsSold_afterBuying_increased(self):
#         before = self.page_under_test.tickets_sold
#         self._fill_form_with_valid_values(self.page_under_test, tickets_to_buy=3)
#         confirm_page = self.page_under_test.submit_form()
#         confirm_page.submit_form()
#         self.driver.get(self.url_to_test)
#         self.page_under_test = pageobjects.PartyPageObject(self.driver)
#         after = self.page_under_test.tickets_sold
#         self.assertEqual(before + 3, after)

#     @classmethod
#     def _fill_form_with_valid_values(cls, page, tickets_to_buy=4, ticket_type=3):
#         page.firstname = 'Kristin'
#         page.lastname = 'Kuche'
#         page.comment = 'Just testing ...'
#         page.email = 'kristin.kuche@gmx.net'
#         page.ticket_count = tickets_to_buy
#         page.ticket_type = ticket_type


# class CashpointTests(SeleniumTestBase):
#     @classmethod
#     def setUpClass(cls):
#         super(CashpointTests, cls).setUpClass()
#         cls.driver = webdriver.Firefox()  # PhantomJS()
#         cls.url_to_test = 'http://localhost:6544/kasse'
#         cls.driver.implicitly_wait(10)  # seconds
#         cls.driver.get(cls.url_to_test)
#         cls.login_page = pageobjects.LoginPageObject(cls.driver)
#         cls.login_page.login = "rut"
#         cls.login_page.password = "berries"
#         cls.login_page.submit_form()

#     def setUp(self):
#         self.driver.get('http://localhost:6544/dashboard/0')
#         self.test_code = pageobjects.DashboardPageObject(self.driver).last_code
#         self.invalid_test_code = 'foobarbaz'
#         self.driver.get(self.url_to_test)
#         self.page_under_test = pageobjects.CashPointPageObject(self.driver)

#     def test_validCode_checkInPageShown(self):
#         self.page_under_test.enter_code(self.test_code)
#         checkin_page = self.page_under_test.submit_form()
#         self.assertTrue(pageobjects.PayPage is checkin_page.__class__ or
#                         pageobjects.CheckInPageObject is checkin_page.__class__)

#     def test_invalidCode_stillOnCashpointPage(self):
#         self.page_under_test.enter_code(self.invalid_test_code)
#         page = self.page_under_test.submit_form()
#         self.assertIs(pageobjects.CashPointPageObject, page.__class__)

#    @classmethod
#    def tearDownClass(cls):
#        super(CashpointTests, cls).tearDownClass()
#        cls.driver.quit()


class CheckInPageTests(SeleniumTestBase):
    @classmethod
    def setUpClass(cls):
        super(CheckInPageTests, cls).setUpClass()
        cls.driver = webdriver.PhantomJS() # Firefox()
        cls.url_to_test = 'http://localhost:6544/kasse'
        cls.driver.implicitly_wait(10)  # seconds
        cls.driver.get(cls.url_to_test)
        cls.login_page = pageobjects.LoginPageObject(cls.driver)
        cls.login_page.login = "rut"
        cls.login_page.password = "berries"
        cls.login_page.submit_form()

    def setUp(self):
        self.driver.get('http://localhost:6544/lu/TR00107635121GP/yes@c3s.cc')
        ticket_page = pageobjects.PartyPageObject(self.driver)
        #PartyFormTests._fill_form_with_valid_values(party_page, tickets_to_buy=5, ticket_type=1)
        PartyFormTests._fill_form_with_valid_values(
            ticket_page, tickets_to_buy=1, ticket_type=1)
        confirm_page = ticket_page.submit_form()
        confirm_page.submit_form()
        self.driver.get('http://localhost:6544/dashboard/0')
        dashboard_page = pageobjects.DashboardPageObject(self.driver)
        dashboard_page = dashboard_page.change_num_to_show(1000)
        self.test_code = dashboard_page.last_code
        self.driver.get(self.url_to_test)
        self.cashpoint_page = pageobjects.CashPointPageObject(self.driver)
        self.cashpoint_page.enter_code(self.test_code)
        self.page_under_test = self.cashpoint_page.submit_form()

    #def test_checkin(self):
    #    already_checked_in_before = self.page_under_test.already_checked_in
    #    checkin_page = self.page_under_test.paid()
    #    checkin_page.persons_to_checkin = 2
    #    checkin_page = checkin_page.checkin()
    #    self.assertTrue(checkin_page.already_checked_in, already_checked_in_before + 2)
    #    self.assertTrue(checkin_page.already_checked_in_this_ticket, 2)
    #    self.assertTrue(checkin_page.tickets_bought, 5)
    #    checkin_page.persons_to_checkin = 3
    #    checkin_page = checkin_page.checkin()
    #    self.assertTrue(checkin_page.already_checked_in, already_checked_in_before + 5)
    #    self.assertTrue(checkin_page.already_checked_in_this_ticket, 5)
    #    self.assertFalse(checkin_page.has_submit_button)

    @classmethod
    def tearDownClass(cls):
        super(CheckInPageTests, cls).tearDownClass()
        cls.driver.quit()
