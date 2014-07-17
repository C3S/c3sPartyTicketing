# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException

__author__ = 'Kristin Kuche'


class PartyPageObject(object):
    def __init__(self, driver):
        self.driver = driver
        #self.firstname_field = self.driver.find_element_by_name("firstname")
        #self.lastname_field = self.driver.find_element_by_name("lastname")
        #self.email_field = self.driver.find_element_by_name("email")
        self.comment_field = self.driver.find_element_by_id("comment")
        self.submit_button = self.driver.find_element_by_id("deformsubmit")
        #self.tickets_count_field = self.driver.find_element_by_id("num_tickets")
        #self.tickets_sold_field = self.driver.find_element_by_id("qty_tickets_sold")

    def submit_form(self):
        self.submit_button.click()
        if 'confirm' in self.driver.current_url:
            return ConfirmPageObject(self.driver)
        return PartyPageObject(self.driver)

    # @property
    # def firstname(self):
    #     return self.firstname_field.get_attribute('value')

    # @firstname.setter
    # def firstname(self, value):
    #     self.firstname_field.send_keys(value)

    # @property
    # def lastname(self):
    #     return self.lastname_field.get_attribute('value')

    # @lastname.setter
    # def lastname(self, value):
    #     self.lastname_field.send_keys(value)

    # @property
    # def email(self):
    #     return self.email_field.get_attribute('value')

    # @email.setter
    # def email(self, value):
    #     self.email_field.send_keys(value)

    @property
    def comment(self):
        return self.comment_field.get_attribute('value')

    @comment.setter
    def comment(self, value):
        self.comment_field.send_keys(value)

    @property
    def ticket_count(self):
        return int(self.tickets_count_field.get_attribute('value'))

    @ticket_count.setter
    def ticket_count(self, value):
        x_path = "option[@value='{0}']".format(value)
        self.tickets_count_field\
            .find_element_by_xpath(x_path).click()

    @property
    def ticket_type(self):
        options = [x for x in self.driver.find_elements_by_name("ticket_type")]
        for opt in options:
            if opt.get_attribute('selected'):
                return int(opt.get_attribute('value'))

    @ticket_type.setter
    def ticket_type(self, value):
        options = [x for x in self.driver.find_elements_by_name("ticket_type")]
        for opt in options:
            if int(opt.get_attribute('value')) == value:
                opt.click()
                return

    @property
    def tickets_sold(self):
        return int(self.tickets_sold_field.text)


class LoginPageObject(object):

    def __init__(self, driver):
        self.driver = driver
        self.submit_button = self.driver.find_element_by_id("deformsubmit")
        self.login_field = self.driver.find_element_by_id("login")
        self.password_field = self.driver.find_element_by_id("password")

    @property
    def login(self):
        return self.login_field.get_attribute('value')

    @login.setter
    def login(self, value):
        self.login_field.send_keys(value)

    @property
    def password(self):
        return self.password_field.get_attribute('value')

    @password.setter
    def password(self, value):
        self.password_field.send_keys(value)

    def submit_form(self):
        self.submit_button.click()
        return CashPointPageObject(self.driver)


class ConfirmPageObject(object):
    def __init__(self, driver):
        self.driver = driver
        self.submit_button = self.driver.find_element_by_id("deformsendmail")

    def submit_form(self):
        # ToDo: Return matching PageObject.
        self.submit_button.click()


class GuestsCountingPageObject(object):
    def __init__(self, driver):
        self.driver = driver
        self.already_checked_in_field = self.driver.find_element_by_id("already_checked_in")
        self.still_awaiting_field = self.driver.find_element_by_id("still_awaiting")

    @property
    def already_checked_in(self):
        return int(self.already_checked_in_field.text)

    @property
    def still_awaiting(self):
        return int(self.still_awaiting_field.text)


class CashPointPageObject(GuestsCountingPageObject):
    def __init__(self, driver):
        super(CashPointPageObject, self).__init__(driver)
        self.code_input_field = self.driver.find_element_by_id('deformField1')
        self.submit_form_btn = self.driver.find_element_by_id('deformgo!')

    def submit_form(self):
        self.submit_form_btn.click()
        # ToDo: Find a better way to determine which page object should be returned
        if '/kasse' in self.driver.current_url:
            return CashPointPageObject(self.driver)
        else:
            return PayPage(self.driver)

    def enter_code(self, code):
        self.code_input_field.send_keys(code)


class PayPage(GuestsCountingPageObject):

    def __init__(self, driver):
        super(PayPage, self).__init__(driver)
        try:
            self._has_paid_btn = self.driver.find_element_by_xpath('/html/body/div[2]/div/form/input[1]')
        except NoSuchElementException:
            pass

    def paid(self):
        self._has_paid_btn.click()
        return CheckInPageObject(self.driver)


class CheckInPageObject(GuestsCountingPageObject):
    def __init__(self, driver):
        super(CheckInPageObject, self).__init__(driver)
        self.has_submit_button = True
        try:
            self._checkin_btn = self.driver.find_element_by_id('checkin-btn')
        except NoSuchElementException, ex:
            self.has_submit_button = False

        try:
            self._persons_select_field = self.driver.find_element_by_name('persons')
        except NoSuchElementException, ex:
            pass
        try:
            self._qty_tickets_field = self.driver.find_element_by_id('num_tickets')
        except NoSuchElementException, ex:
            pass
        self._already_checked_in_persons_field = self.driver.find_element_by_id('checked_in_persons')

    @property
    def persons_to_checkin(self):
         return int(self._persons_select_field.get_attribute('value'))

    @persons_to_checkin.setter
    def persons_to_checkin(self, qty):
        x_path = "option[@value='{0}']".format(qty)
        self._persons_select_field\
            .find_element_by_xpath(x_path).click()

    def checkin(self):
        assert(self._checkin_btn is not None)
        self._checkin_btn.click()
        return CheckInPageObject(self.driver)

    @property
    def tickets_bought(self):
        return self._qty_tickets_field.text

    @property
    def already_checked_in_this_ticket(self):
        return self._already_checked_in_persons_field.text


class DashboardPageObject(object):
    def __init__(self, driver):
        self.driver = driver
        self._first_code_field = self.driver.find_element_by_xpath('//*[@id="main"]/table/tbody/tr[2]/td[2]/a')
        self._last_code_field = self.driver.find_element_by_css_selector('#main table tr:last-child td:nth-child(2) a')
        self._num_to_show_field = self.driver.find_element_by_id('num_to_show')

    @property
    def first_code(self):
        return self._first_code_field.text

    @property
    def last_code(self):
        return self._last_code_field.text

    def change_num_to_show(self, to_show):
        self._num_to_show_field.send_keys(str(to_show) + "\n")
        return DashboardPageObject(self.driver)
