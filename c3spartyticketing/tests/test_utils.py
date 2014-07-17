# -*- coding: utf-8  -*-
from datetime import date
import os
from pyramid import testing
from sqlalchemy import engine_from_config
#import subprocess
#from subprocess import CalledProcessError
import transaction
import unittest

from c3spartyticketing.models import (
    DBSession,
    Base,
    PartyTicket
)


class TestUtilities(unittest.TestCase):
    """
    tests for c3spartyticketing/utils.py
    """
    def setUp(self):
        """
        set up everything for a test case
        """
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.close()
            DBSession.remove()
            #print("removing old DBSession =================================")
        except:
            #print("no DBSession to remove =================================")
            pass
        test_settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'available_languages': 'da de en es fr',
            'mailrecipient': 'c@c3s.cc',
            'mail.debug': True,
        }
        engine = engine_from_config(test_settings)
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.req = testing.DummyRequest()
        with transaction.manager:
            ticket1 = PartyTicket(
                token=u'TESTTOKEN456',
                firstname=u'SomeFirstnäme',
                lastname=u'SomeLastnäme',
                email=u'some@shri.de',
                password=u'arandompassword',
                locale=u"de",
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGBAR',
                date_of_submission=date.today(),
                num_tickets=1,
                ticket_gv_attendance=1,
                ticket_bc_attendance=True,
                ticket_bc_buffet=True,
                ticket_tshirt=True,
                ticket_tshirt_type=u'm',
                ticket_tshirt_size=u'xxl',
                ticket_all=False,
                ticket_support=False,
                ticket_support_x=False,
                ticket_support_xl=False,
                support=0,
                discount=0,
                the_total=75,
                rep_firstname=u'first',
                rep_lastname=u'last',
                rep_street=u'street',
                rep_zip=u'zip',
                rep_city=u'city',
                rep_country=u'country',
                rep_type=u'sibling',
                guestlist=False,
                user_comment=u"äh, was?"
            )
            DBSession.add(ticket1)
            DBSession.flush()

    def tearDown(self):
        """
        clean up after a test case
        """
        DBSession.close()
        DBSession.remove()
        testing.tearDown()
        #os.remove('test_utils.db')

    def test_make_random_string(self):
        from c3spartyticketing.utils import make_random_string
        _string = make_random_string()
        #print "the _string: {}".format(_string)
        #print "the _string length: {}".format(len(_string))
        #print dir(_string)
        #self.assertTrue()

    def test_generate_qr_code(self):
        """
        Test QR-Code generation
        """
        from c3spartyticketing.utils import make_qr_code_pdf
        _ticket = PartyTicket.get_by_id(1)
        result = make_qr_code_pdf(
            _ticket,
            "http://192.168.2.128:6544/ci/p1402/ABCDEFGBAR")
        result

    def test_make_qr_code_pdf_mobile(self):
        """
        Test QR-Code generation for mobile
        """
        from c3spartyticketing.utils import make_qr_code_pdf_mobile
        _ticket = PartyTicket.get_by_id(1)
        #import pdb
        #pdb.set_trace()
        self.req.registry.settings[
            'ticket_pdf'] = 'pdftk/C3S_Ticket_BCGV.pdf'
        result = make_qr_code_pdf_mobile(
            #self.req,
            _ticket,
            "http://192.168.2.128:6544/ci/p1402/ABCDEFGBAR")
        result

        #_img = result.save('r2d2.png')
        #print("size of the resulting PDF: %s" % len(result))
        #import pdb
        #pdb.set_trace()
        # XXX what can we assert here?

    #def test_make_ticket_confirmation_emailbody(self):
    #    from c3spartyticketing.utils import (
    #        make_ticket_confirmation_emailbody
    #    )
    #    res = make_ticket_confirmation_emailbody('foo')

    # def test_generate_pdf_en(self):
    #     """
    #     Test pdf generation
    #     and resulting pdf size
    #     """
    #     from c3spartyticketing.views import generate_pdf

    #     mock_appstruct = {
    #         'firstname': u'Anne',
    #         'lastname': u'Gilles',
    #         'email': u'devnull@c3s.cc',
    #         'email_confirm_code': u'1234567890',
    #         'date_of_birth': '1987-06-05',
    #         'ticket_type': 1,
    #         'num_tickets': 10,
    #         'the_total': 50,
    #         '_LOCALE_': 'en',
    #         'date_of_submission': '2013-09-09 08:44:47.251588',
    #     }

    #     # a skipTest iff pdftk is not installed
    #     try:
    #         res = subprocess.check_call(
    #             ["which", "pdftk"], stdout=None)
    #         if res == 0:
    #             # go ahead with the tests
    #             result = generate_pdf(mock_appstruct)

    #             self.assertEquals(result.content_type,
    #                               'application/pdf')
    #             #print("size of pdf: " + str(len(result.body)))
    #             # check pdf size
    #             self.assertTrue(120000 > len(result.body) > 50000)

    #             # TODO: check pdf for contents

    #     except CalledProcessError, cpe:  # pragma: no cover
    #         print("pdftk not installed. skipping test!")
    #         print(cpe)

    # def test_generate_pdf_de(self):
    #     """
    #     Test pdf generation
    #     and resulting pdf size
    #     """
    #     from c3spartyticketing.views import generate_pdf

    #     mock_appstruct = {
    #         'firstname': u'Anne',
    #         'lastname': u'Gilles',
    #         'address1': u'addr one',
    #         'address2': u'addr two',
    #         'postcode': u'54321',
    #         'city': u'Müsterstädt',
    #         'email': u'devnull@c3s.cc',
    #         'email_confirm_code': u'1234567890',
    #         'date_of_birth': u'1987-06-05',
    #         'country': u'my country',
    #         'membership_type': 'investing',
    #         'num_shares': u'23',
    #         '_LOCALE_': 'de',
    #         'date_of_submission': '2013-09-09 08:44:47.251588',
    #     }

    #     # a skipTest iff pdftk is not installed
    #     import subprocess
    #     from subprocess import CalledProcessError
    #     try:
    #         res = subprocess.check_call(
    #             ["which", "pdftk"], stdout=None)
    #         if res == 0:
    #             # go ahead with the tests
    #             result = generate_pdf(mock_appstruct)

    #             self.assertEquals(result.content_type,
    #                               'application/pdf')
    #             #print("size of pdf: " + str(len(result.body)))
    #             #print(result)
    #             # check pdf size
    #             self.assertTrue(120000 > len(result.body) > 50000)

    #             # TODO: check pdf for contents

    #     except CalledProcessError, cpe:  # pragma: no cover
    #         print("pdftk not installed. skipping test!")
    #         print(cpe)

#     def test_generate_csv(self):
#         """
#         test creation of csv snippet
#         """
#         from c3spartyticketing.utils import generate_csv
#         my_appstruct = {
#             'firstname': 'Jöhn',
#             'lastname': 'Doe',
#             'address1': 'In the Middle',
#             'address2': 'Of Nowhere',
#             'postcode': '12345',
#             'city': 'My Town',
#             'email': 'devnull@c3s.cc',
#             'email_confirm_code': u'1234567890',
#             'country': 'de',
#             'date_of_birth': '1987-06-05',
#             'member_of_colsoc': 'yes',
#             'name_of_colsoc': 'GEMA FöTT',
#             'membership_type': 'investing',
#             'num_shares': "25"
#         }
#         result = generate_csv(my_appstruct)
#         #print("test_generate_csv: the result: %s") % result
#         from datetime import date
#         today = date.today().strftime("%Y-%m-%d")
#         expected_result = today + ',pending...,Jöhn,Doe,devnull@c3s.cc,1234567890,In the Middle,Of Nowhere,12345,My Town,de,investing,1987-06-05,j,GEMA FöTT,25\r\n'
#         # note the \r\n at the end: that is line-ending foo!

#         #print("type of today: %s ") % type(today)
#         #print("type of result: %s ") % type(result)
#         #print("type of expected_result: %s ") % type(expected_result)
#         #print("result: \n%s ") % (result)
#         #print("expected_result: \n%s ") % (expected_result)
#         self.assertEqual(str(result), str(expected_result))

# #            result == str(today + ';unknown;pending...;John;Doe;' +
# #                          'devnull@c3s.cc;In the Middle;Of Nowhere;' +
# #                          '12345;My Town;Hessen;de;j;n;n;n;n;j;j;j;j;j;j'))

    # def test_mail_body(self):
    #     """
    #     test if mail body is constructed correctly
    #     and if umlauts work
    #     """
    #     from c3spartyticketing.utils import make_mail_body
    #     import datetime
    #     dob = datetime.date(1999, 1, 1)
    #     my_appstruct = {
    #         'activity': [u'composer', u'dj'],
    #         'firstname': u'Jöhn test_mail_body',
    #         'lastname': u'Döe',
    #         'date_of_birth': dob,
    #         'address1': u'addr one',
    #         'address2': u'addr two',
    #         'postcode': u'12345 xyz',
    #         'city': u'Town',
    #         'email': u'devnull@c3s.cc',
    #         'email_confirm_code': u'1234567890',
    #         'country': u'af',
    #         'member_of_colsoc': u'yes',
    #         'name_of_colsoc': u'Buma',
    #         'membership_type': u'investing',
    #         'num_shares': u"23",
    #     }
    #     result = make_mail_body(my_appstruct)

    #     self.failUnless(u'Jöhn test_mail_body' in result)
    #     self.failUnless(u'Döe' in result)
    #     self.failUnless(u'postcode:                       12345 xyz' in result)
    #     self.failUnless(u'Town' in result)
    #     self.failUnless(u'devnull@c3s.cc' in result)
    #     self.failUnless(u'af' in result)
    #     self.failUnless(u'number of shares                23' in result)
    #     self.failUnless(
    #         u'member of coll. soc.:           yes' in result)
    #     self.failUnless(u"that's it.. bye!" in result)

    # def test_accountant_mail(self):
    #     """
    #     test creation of email Message object
    #     """
    #     from c3sintent.utils import accountant_mail
    #     import datetime
    #     my_appstruct = {
    #         'activity': [u'composer', u'dj'],
    #         'firstname': u'Jöhn test_accountant_mail',
    #         'lastname': u'Doe',
    #         'date_of_birth': datetime.date(1987, 6, 5),
    #         'city': u'Town',
    #         'email': u'devnull@example.com',
    #         'country': u'af',
    #         'member_of_colsoc': u'yes',
    #         'name_of_colsoc': u'Foo Colsoc',
    #         'invest_member': u'yes',
    #         'opt_URL': u'http://the.yes',
    #         'opt_band': u'the yes',
    #         'noticed_dataProtection': u'yes'
    #     }
    #     result = accountant_mail(my_appstruct)

    #     from pyramid_mailer.message import Message

    #     self.assertTrue(isinstance(result, Message))
    #     self.assertTrue('yes@c3s.cc' in result.recipients)
    #     self.failUnless('-----BEGIN PGP MESSAGE-----' in result.body,
    #                     'something missing in the mail body!')
    #     self.failUnless('-----END PGP MESSAGE-----' in result.body,
    #                     'something missing in the mail body!')
    #     self.failUnless(
    #         '[C3S] Yes! a new letter of intent' in result.subject,
    #         'something missing in the mail body!')
    #     self.failUnless('noreply@c3s.cc' == result.sender,
    #                     'something missing in the mail body!')
