# -*- coding: utf-8  -*-
import os
import unittest
import transaction
#from pyramid.config import Configurator
from pyramid import testing
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from c3spartyticketing.models import (
    DBSession,
    Base,
    PartyTicket,
    Group,
    C3sStaff,
)
DEBUG = False


class PartyTicketTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
            #print("removing old DBSession")
        except:
            #print("no DBSession to remove")
            pass
        #engine = create_engine('sqlite:///test_models.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        DBSession.configure(bind=engine)  # XXX does influence self.session!?!
        Base.metadata.create_all(engine)
        with transaction.manager:
            ticket1 = PartyTicket(  # german
                token='TESTTOKEN123',
                firstname=u'SomeFirstnäme',
                lastname=u'SomeLastnäme',
                email=u'some@shri.de',
                password='not_set',
                locale=u"de",
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFOO',
                date_of_submission=date.today(),
                num_tickets=1,
                user_comment=u'foo comment',
                the_total=15,
                ticket_gv_attendance=1,
                ticket_bc_attendance=True,
                ticket_bc_buffet=True,
                ticket_tshirt=False,
                ticket_tshirt_type=0,
                ticket_tshirt_size=0,
                ticket_all=False,
                ticket_support=False,
                ticket_support_x=False,
                ticket_support_xl=False,
                support=0,
                discount=0,
                rep_firstname=u'',
                rep_lastname=u'',
                rep_street=u'',
                rep_zip=u'',
                rep_city=u'',
                rep_country=u'',
                rep_type=u'',
                guestlist=False,
            )
            DBSession.add(ticket1)
            DBSession.flush()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        #os.remove('test_models.db')

    def _getTargetClass(self):
        from c3spartyticketing.models import PartyTicket
        return PartyTicket

    def _makeOne(self,
                 token=u'TESTTOKEN123',
                 firstname=u'SomeFirstnäme',
                 lastname=u'SomeLastnäme',
                 email=u'some@shri.de',
                 password=u'noneset',
                 locale=u"DE",
                 email_is_confirmed=False,
                 email_confirm_code=u'ABCDEFGHIK',
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
                 the_total=15,
                 rep_firstname=u'first',
                 rep_lastname=u'last',
                 rep_street=u'street',
                 rep_zip=u'zip',
                 rep_city=u'city',
                 rep_country=u'country',
                 rep_type=u'sibling',
                 guestlist=False,
                 user_comment=u'foo',
                 ):
        #print "type(self.session): " + str(type(self.session))
        return self._getTargetClass()(  # order of params DOES matter
            token,
            firstname,
            lastname,
            email,
            password,
            locale,
            email_is_confirmed,
            email_confirm_code,
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
            rep_firstname,
            rep_lastname,
            rep_street,
            rep_zip,
            rep_city,
            rep_country,
            rep_type,
            guestlist,
            user_comment,
        )

    def _makeAnotherOne(self,
                        token=u'TESTTOKEN456',
                        firstname=u'SomeFirstnäme',
                        lastname=u'SomeLastname',
                        email=u'some@shri.de',
                        password=u'arandompassword',
                        locale=u"de",
                        email_is_confirmed=False,
                        email_confirm_code=u'0987654321',
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
                        the_total=150,
                        rep_firstname=u'first',
                        rep_lastname=u'last',
                        rep_street=u'street',
                        rep_zip=u'zip',
                        rep_city=u'city',
                        rep_country=u'country',
                        rep_type=u'sibling',
                        guestlist=False,
                        user_comment=u'bar',
                        ):
        return self._getTargetClass()(  # order of params DOES matter
            token,
            firstname,
            lastname,
            email,
            password,
            locale,
            email_is_confirmed,
            email_confirm_code,
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
            rep_firstname,
            rep_lastname,
            rep_street,
            rep_zip,
            rep_city,
            rep_country,
            rep_type,
            guestlist,
            user_comment,
        )

    def test_constructor(self):
        instance = self._makeOne()
        print(instance.firstname)
        self.assertEqual(instance.firstname, u'SomeFirstnäme', "No match!")
        self.assertEqual(instance.lastname, u'SomeLastnäme', "No match!")
        self.assertEqual(instance.email, u'some@shri.de', "No match!")
        self.assertEqual(instance.email, u'some@shri.de', "No match!")
        self.assertEqual(
            instance.email_confirm_code, u'ABCDEFGHIK', "No match!")
        self.assertEqual(instance.email_is_confirmed, False, "expected False")
        #self.assertEqual(instance.ticket_type, 3, "No match!")

    def test_get_by_code(self):
        instance = self._makeOne()
        self.session.add(instance)
        myTestClass = self._getTargetClass()
        instance_from_DB = myTestClass.get_by_code(u'ABCDEFGHIK')
        self.assertEqual(instance.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_token(self):
        instance = self._makeOne()
        self.session.add(instance)
        #self.session.flush()
        myTestClass = self._getTargetClass()
        instance_from_DB = myTestClass.get_by_token(u'TESTTOKEN123')
        self.assertEqual(instance.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')

    def test_get_by_id(self):
        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush()
        _id = instance.id
        _date_of_submission = instance.date_of_submission
        myClass = self._getTargetClass()
        instance_from_DB = myClass.get_by_id(_id)
        if DEBUG:
            print "myClass: " + str(myClass)
        self.assertEqual(instance_from_DB.firstname, u'SomeFirstnäme')
        self.assertEqual(instance_from_DB.lastname, u'SomeLastnäme')
        self.assertEqual(instance_from_DB.email, u'some@shri.de')
        self.assertEqual(instance_from_DB.locale, u'DE')
        self.assertEqual(instance_from_DB.email_is_confirmed, False)
        self.assertEqual(instance_from_DB.email_confirm_code, u'ABCDEFGHIK')
        self.assertEqual(instance_from_DB.date_of_submission, _date_of_submission)
        self.assertEqual(instance_from_DB.num_tickets, 1)

    def test_delete_by_id(self):
        instance = self._makeOne()
        #session = DBSession()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        instance_from_DB = myMembershipSigneeClass.get_by_id('1')
        del_instance_from_DB = myMembershipSigneeClass.delete_by_id('1')
        #print del_instance_from_DB
        instance_from_DB = myMembershipSigneeClass.get_by_id('1')
        self.assertEqual(None, instance_from_DB)

    def test_check_user_or_None(self):
        instance = self._makeOne()
        #session = DBSession()
        self.session.add(instance)
        myMembershipSigneeClass = self._getTargetClass()
        # get first dataset (id = 1)
        result1 = myMembershipSigneeClass.check_user_or_None('1')
        #print check_user_or_None
        self.assertEqual(1, result1.id)
        # get invalid dataset
        result2 = myMembershipSigneeClass.check_user_or_None('1234567')
        #print check_user_or_None
        self.assertEqual(None, result2)

    def test_check_for_existing_confirm_code(self):
        instance = self._makeOne()
        self.session.add(instance)
        myClass = self._getTargetClass()

        result1 = myClass.check_for_existing_confirm_code(
            u'ABCDEFGHIK')
        #print result1  # True
        self.assertEqual(result1, True)
        result2 = myClass.check_for_existing_confirm_code(
            u'ABCDEFGHIK0000000000')
        #print result2  # False
        self.assertEqual(result2, False)

    def test_listing(self):
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myClass = self._getTargetClass()

        result = myClass.ticket_listing(
            myClass.id.desc())
        self.failUnless(result[0].firstname == u"SomeFirstnäme")
        self.failUnless(result[1].firstname == u"SomeFirstnäme")
        print (result[2].firstname)
        self.failUnless(result[2].firstname == u"SomeFirstnäme")

    def test_get_all_codes(self):
        instance = self._makeOne()
        self.session.add(instance)
        instance2 = self._makeAnotherOne()
        self.session.add(instance2)
        myClass = self._getTargetClass()

        result = myClass.get_all_codes()
        #print result1
        self.assertTrue(len(result) is 3)
        self.assertTrue(u'ABCDEFGFOO' in result)
        self.assertTrue(u'ABCDEFGHIK' in result)
        self.assertTrue(u'0987654321' in result)

    def test_get_number(self):
        myClass = self._getTargetClass()
        result = myClass.get_number()
        #print result1
        self.assertEqual(result, 1)

    def test_get_num_tickets(self):
        myClass = self._getTargetClass()
        result = myClass.get_num_tickets()
        self.assertEqual(result, 1)

        instance = self._makeOne()
        self.session.add(instance)
        self.session.flush()
        result2 = myClass.get_num_tickets()
        self.assertEqual(result2, 2)

    # def test_num_passengers(self):
    #     myClass = self._getTargetClass()
    #     result = myClass.num_passengers()
    #     self.assertEqual(result, 0)

    #     instance = self._makeOne()
    #     self.session.add(instance)
    #     self.session.flush()
    #     result2 = myClass.num_passengers()
    #     self.assertEqual(result2, 4)


class GroupTests(unittest.TestCase):
    """
    test the groups
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        #engine = create_engine('sqlite:///test_model_groups.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            group1 = Group(name=u'testgroup')
            DBSession.add(group1)
            DBSession.flush()
            self.assertEquals(group1.__str__(), 'group:testgroup')

    def tearDown(self):
        self.session.close()
        self.session.remove()
        #os.remove('test_model_groups.db')

    def test_group(self):
        cashiers_group = Group(name=u'kasse')
        self.session.add(cashiers_group)

        result = Group.get_cashiers_group()
        self.assertEquals(result.__str__(), 'group:kasse')


class C3sStaffTests(unittest.TestCase):
    """
    test the staff and cashiers accounts
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        #engine = create_engine('sqlite:///test_model_staff.db')
        engine = create_engine('sqlite://')
        self.session = DBSession
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            group1 = Group(name=u'staff')
            group2 = Group(name=u'kasse')
            DBSession.add(group1, group2)
            DBSession.flush()

    def tearDown(self):
        self.session.close()
        self.session.remove()
        #os.remove('test_model_staff.db')

    def test_staff(self):
        staffer1 = C3sStaff(
            login=u'staffer1',
            password=u'stafferspassword'
        )
        staffer1.group = ['staff']
        cashier1 = C3sStaff(
            login=u'cashier1',
            password=u'stafferspassword',
        )
        cashier1.group = ['kasse']

        self.session.add(staffer1)
        self.session.add(cashier1)
        self.session.flush()

        _cashier1_id = cashier1.id
        _staffer1_id = staffer1.id

        self.assertTrue(cashier1.password is not '')

        #print('by id: %s' % C3sStaff.get_by_id(_staffer1_id))
        #print('by id: %s' % C3sStaff.get_by_id(_cashier1_id))
        #print('by login: %s' % C3sStaff.get_by_login(u'staffer1'))
        #print('by login: %s' % C3sStaff.get_by_login(u'cashier1'))
        self.assertEqual(
            C3sStaff.get_by_id(_staffer1_id),
            C3sStaff.get_by_login(u'staffer1')
        )
        self.assertEqual(
            C3sStaff.get_by_id(_cashier1_id),
            C3sStaff.get_by_login(u'cashier1')
        )

        '''test get_all'''
        res = C3sStaff.get_all()
        self.assertEqual(len(res), 2)

        '''test delete_by_id'''
        C3sStaff.delete_by_id(1)
        res = C3sStaff.get_all()
        self.assertEqual(len(res), 1)

        '''test check_user_or_None'''
        res1 = C3sStaff.check_user_or_None(u'cashier1')
        res2 = C3sStaff.check_user_or_None(u'staffer1')
        #print res1
        #print res2
        self.assertTrue(res1 is not None)
        self.assertTrue(res2 is None)

        '''test check_password'''
        #print(C3sStaff.check_password(cashier1, 'cashierspassword'))
        C3sStaff.check_password(u'cashier1', u'cashierspassword')
        #self.assert
