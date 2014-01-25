# -*- coding: utf-8 -*-
__author__ = 'Kristin Kuche'


class PartyPageObject(object):
    def __init__(self, driver):
        self.driver = driver
        self.firstname_field = self.driver.find_element_by_name("firstname")
        self.lastname_field = self.driver.find_element_by_name("lastname")
        self.email_field = self.driver.find_element_by_name("email")
        self.comment_field = self.driver.find_element_by_id("comment")
        self.submit_button = self.driver.find_element_by_id("deformsubmit")
        self.tickets_count_field = self.driver.find_element_by_id("num_tickets")


    def submit_form(self):
        self.submit_button.click()
        return PartyPageObject(self.driver)

    @property
    def firstname(self):
        return self.firstname_field.get_attribute('value')

    @firstname.setter
    def firstname(self, value):
        self.firstname_field.send_keys(value)

    @property
    def lastname(self):
        return self.lastname_field.get_attribute('value')

    @lastname.setter
    def lastname(self, value):
        self.lastname_field.send_keys(value)

    @property
    def email(self):
        return self.email_field.get_attribute('value')

    @email.setter
    def email(self, value):
        self.email_field.send_keys(value)

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