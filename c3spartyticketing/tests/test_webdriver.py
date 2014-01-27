# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver
import time
from subprocess import call
import pageobjects
__author__ = 'Kristin Kuche'


class SeleniumTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        call(['env/bin/pserve', 'development.ini', 'start'])
        time.sleep(3)

    def setUp(self):
        pass

    @classmethod
    def tearDownClass(cls):
        call(['env/bin/pserve', 'development.ini', 'stop'])


class PartyFormTests(SeleniumTestBase):

    @classmethod
    def setUpClass(cls):
        super(PartyFormTests, cls).setUpClass()
        cls.driver = webdriver.Firefox()  # PhantomJS()
        cls.url_to_test = 'http://localhost:6544/'
        cls.driver.get(cls.url_to_test)
        cls.driver.implicitly_wait(10)  # seconds

    @classmethod
    def tearDownClass(cls):
        super(PartyFormTests, cls).setUpClass()
        cls.driver.quit()

    def setUp(self):
        super(PartyFormTests, self).setUp()
        self.driver.get('http://localhost:6544/')
        self.page_under_test = pageobjects.PartyPageObject(self.driver)

    def test_form_submission(self):
        self.page_under_test.firstname_field.send_keys('Kristin')
        self.page_under_test = self.page_under_test.submit_form()
        self.assertEqual('Kristin', self.page_under_test.firstname_field.get_attribute('value'))

    def test_submitEmptyForm_errorShown(self):
        self.page_under_test = self.page_under_test.submit_form()
        self.assertIsNotNone(self.driver.find_element_by_id('error-lastname'))
        self.assertIsNotNone(self.driver.find_element_by_id('error-firstname'))
        self.assertIsNotNone(self.driver.find_element_by_id('error-email'))

    def test_formIncomplete_errorShown(self):
        self.page_under_test.firstname = 'Kristin'
        self.page_under_test.comment = 'Just testing ...'
        self.page_under_test.ticket_count = 5
        self.page_under_test.ticket_type = 2
        self.assertRaises(Exception, self.driver.find_element_by_id, 'error-lastname')

        self.page_under_test = self.page_under_test.submit_form()

        self.assertEqual('Kristin', self.page_under_test.firstname)
        self.assertEqual('', self.page_under_test.lastname)
        element = self.driver.find_element_by_id('error-lastname')
        self.assertIsNotNone(element)
        self.assertEqual('Just testing ...', self.page_under_test.comment)
        self.assertEqual(5, self.page_under_test.ticket_count)
        self.assertEqual(2, self.page_under_test.ticket_type)

    def test_ticketType1_standardValue1(self):
        value = self.page_under_test.ticket_type
        self.assertEqual(1, value)

    def test_ticketNum_standardValue1(self):
        value = self.page_under_test.ticket_count
        self.assertEqual(1, value)

    def test_ticketsSold_afterBuying_increased(self):
        before = self.page_under_test.tickets_sold
        self._fill_form_with_valid_values(tickets_to_buy=3)
        confirm_page = self.page_under_test.submit_form()
        confirm_page.submit_form()
        self.driver.get(self.url_to_test)
        self.page_under_test = pageobjects.PartyPageObject(self.driver)
        after = self.page_under_test.tickets_sold
        self.assertEqual(before + 3, after)

    def _fill_form_with_valid_values(self, tickets_to_buy=4):
        self.page_under_test.firstname = 'Kristin'
        self.page_under_test.lastname = 'Kuche'
        self.page_under_test.comment = 'Just testing ...'
        self.page_under_test.email = 'kristin.kuche@gmx.net'
        self.page_under_test.ticket_count = tickets_to_buy
        self.page_under_test.ticket_type = 3