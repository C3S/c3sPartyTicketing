# -*- coding: utf-8  -*-
import transaction
#import cryptacular.bcrypt
from datetime import (
    date,
    datetime,
)
import cryptacular.bcrypt

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Index,
    Text,
    Integer,
    Boolean,
    DateTime,
    Date,
    Unicode
)
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    InvalidRequestError
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    synonym
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def hash_password(password):
    return unicode(crypt.encode(password))


class Group(Base):
    """
    groups aka roles for users
    """
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Unicode(30), unique=True, nullable=False)

    def __str__(self):
        return 'group:%s' % self.name

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_cashiers_group(cls, groupname=u'kasse'):
        dbsession = DBSession()
        kasse_group = dbsession.query(
            cls).filter(cls.name == groupname).first()
        #print('=== get_kasse_group:' + str(kasse_group))
        return kasse_group

#    @classmethod
#    def get_Users_group(cls, groupname="User"):
#        """Choose the right group for users"""
#        dbsession = DBSession()
#        users_group = dbsession.query(
#            cls).filter(cls.name == groupname).first()
#        print('=== get_Users_group:' + str(users_group))
#        return users_group


# table for relation between staffers and groups
staff_groups = Table(
    'staff_groups', Base.metadata,
    Column(
        'staff_id', Integer, ForeignKey('staff.id'),
        primary_key=True, nullable=False),
    Column(
        'group_id', Integer, ForeignKey('groups.id'),
        primary_key=True, nullable=False)
)


class C3sStaff(Base):
    """
    C3S staff may login and do things
    """
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    login = Column(Unicode(255))
    _password = Column('password', Unicode(60))
    last_password_change = Column(
        DateTime,
        default=func.current_timestamp())
    email = Column(Unicode(255))
    groups = relationship(
        Group,
        secondary=staff_groups,
        backref="staff")

    def _init_(self, login, password, email):  # pragma: no cover
        self.login = login
        self.password = password
        self.last_password_change = datetime.now()
        self.email = email

    #@property
    #def __acl__(self):
    #    return [
    #        (Allow,                           # user may edit herself
    #         self.username, 'editUser'),
    #        #'user:%s' % self.username, 'editUser'),
    #        (Allow,                           # accountant group may edit
    #         'group:accountants', ('view', 'editUser')),
    #        (Allow,                           # admin group may edit
    #         'group:admins', ('view', 'editUser')),
    #    ]

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_by_login(cls, login):
        return DBSession.query(cls).filter(cls.login == login).first()

    @classmethod
    def delete_by_id(cls, id):
        _del = DBSession.query(cls).filter(cls.id == id).first()
        _del.groups = []
        DBSession.query(cls).filter(cls.id == id).delete()
        return

    @classmethod
    def get_all(cls):
        return DBSession.query(cls).all()

    @classmethod
    def check_password(cls, login, password):
        #dbSession = DBSession()
        staffer = cls.get_by_login(login)
        #if staffer is None:  # ?
        #    return False
        #if not staffer:  # ?
        #    return False
        return crypt.check(staffer.password, password)

    # this one is used by RequestWithUserAttribute
    @classmethod
    def check_user_or_None(cls, login):
        """
        check whether a user by that username exists in the database.
        if yes, return that object, else None.
        returns None if username doesn't exist
        """
        login = cls.get_by_login(login)  # is None if user not exists
        return login


class PartyTicket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    # person info
    firstname = Column(Text)
    lastname = Column(Text)
    email = Column(Unicode(255))
    _password = Column('password', Unicode(60))
    last_password_change = Column(
        DateTime,
        default=func.current_timestamp())
    locale = Column(Unicode(255))
    email_is_confirmed = Column(Boolean, default=False)
    email_confirm_code = Column(Unicode(255), unique=True)
    # ticket info
    tcodes = Column(Unicode(255), unique=True)
    num_tickets = Column(Integer)
    checked_persons = Column(Integer, default=0)
    #ticket_type = Column(Integer)
    ticket_type_tgv = Column(Boolean, default=False)
    ticket_type_tbc = Column(Boolean, default=False)
    ticket_type_vgv = Column(Boolean, default=False)
    ticket_type_vbc = Column(Boolean, default=False)
    ticket_type_ets = Column(Boolean, default=False)
    ticket_type_all = Column(Boolean, default=False)
    guestlist = Column(Boolean, default=False)
    discount = Column(Integer)
    the_total = Column(Integer)
    date_of_submission = Column(DateTime(), nullable=False)
    payment_received = Column(Boolean, default=False)
    payment_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    ticketmail_sent = Column(Boolean, default=False)
    ticketmail_sent_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    user_comment = Column(Unicode(255))
    accountant_comment = Column(Unicode(255))

    def __init__(self, firstname, lastname, email, password,
                 locale,
                 email_is_confirmed, email_confirm_code,
                 date_of_submission,
                 num_tickets,
                 ticket_type_tgv,
                 ticket_type_tbc,
                 ticket_type_vgv,
                 ticket_type_vbc,
                 ticket_type_ets,
                 ticket_type_all,
                 guestlist,
                 discount,
                 the_total,
                 user_comment,
                 payment_received=False
                 ):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.num_tickets = num_tickets
        self.ticket_type_tgv = ticket_type_tgv
        self.ticket_type_tbc = ticket_type_tbc
        self.ticket_type_vgv = ticket_type_vgv
        self.ticket_type_vbc = ticket_type_vbc
        self.ticket_type_ets = ticket_type_ets
        self.ticket_type_all = ticket_type_all
        self.guestlist = guestlist
        self.discount = discount
        self.the_total = the_total
        self.password = password
        self.last_password_change = datetime.now()
        self.locale = locale
        self.email_is_confirmed = email_is_confirmed
        self.email_confirm_code = email_confirm_code
        self.date_of_submission = datetime.now()
        self.payment_received = payment_received
        self.user_comment = user_comment

    #def _get_password(self):
    #    return self._password
    #
    #def _set_password(self, password):
    #    self._password = hash_password(password)

    #password = property(_get_password, _set_password)
    #password = synonym('_password', descriptor=password)

    @classmethod
    def get_by_code(cls, email_confirm_code):
        """
        find a member by email confirmation code

        this is needed when a user returns from reading her email
        and clicking on a link containing the confirmation code.
        as the code is unique, one record is returned.
        """
        return DBSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()

    #@classmethod
    #def get_by_tcode(cls, tcode):
    #    """
    #    find a member by ticket code
    #    """
    #    return DBSession.query(cls).filter(
    #        cls.email_confirm_code == tcode).first()

    @classmethod
    def get_all_codes(cls):
        """
        get all the codes
        this is needed when a staffer searches for codes using autocomplete
        """
        all = DBSession.query(cls).all()
        codes = []
        for item in all:
            codes.append(item.email_confirm_code)
        #print("codes before returning from classmethod: %s" % codes)
        return codes

    @classmethod
    def check_for_existing_confirm_code(cls, email_confirm_code):
        """
        check if a code is already present
        """
        check = DBSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()
        if check:  # pragma: no cover
            return True
        else:
            return False

    # @classmethod
    # def check_for_existing_ticket_code(cls, tcode):
    #     """
    #     check if a code is already present
    #     """
    #     check = DBSession.query(cls).filter(
    #         cls.tcode == tcode).first()
    #     if check:  # pragma: no cover
    #         return True
    #     else:
    #         return False

    @classmethod
    def get_by_id(cls, _id):
        """return one ticket by id"""
        return DBSession.query(cls).filter(cls.id == _id).first()

    @classmethod
    def delete_by_id(cls, _id):
        """return one member by id"""
        return DBSession.query(cls).filter(cls.id == _id).delete()

    @classmethod
    def get_number(cls):
        """return number of database entries (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def get_num_tickets(cls):
        """return number of single people"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            _num = _num + item.num_tickets
        return _num

    @classmethod
    def num_passengers(cls):
        """return number of people already checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            _num = _num + item.checked_persons
        return _num

    @classmethod
    def get_num_unpaid(cls):
        """return number of people/tickets NOT YET paid"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if not item.payment_received:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_tickets_paid(cls):
        """return number of people/tickets PAID, but NOT YET checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.payment_received:
                _num = _num + item.num_tickets
        return _num

    # ticket categories
    # totals
    @classmethod
    def get_num_hobos(cls):
        """return number of hobos"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.guestlist == True:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_hobos_checked(cls):
        """return number of hobos checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 5:
            #(
            #    (item.ticket_type == 5) and
            #        (item.checked_persons is not item.num_tickets)):
                _num = _num + item.checked_persons
        return _num

    @classmethod
    def get_num_class_2(cls):
        """return number people on ticket class 2"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 1:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_2_food(cls):
        """return number people on ticket class 2 with foodstamp"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 2:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_1(cls):
        """return number people on ticket class 1"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 3:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_green(cls):
        """return number people on ticket class green mamba"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 4:
                _num = _num + item.num_tickets
        return _num

    # preorder
    @classmethod
    def get_num_class_2_pre(cls):
        """return number people on ticket class 2 (paid)"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if (
                (item.ticket_type == 1) and
                    (not 'CASHDESK' in item.email_confirm_code) and
                    (item.payment_received)):
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_2_food_pre(cls):
        """return number people on ticket class 2 with foodstamp (paid)"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if (
                (item.ticket_type == 2) and
                    (not 'CASHDESK' in item.email_confirm_code) and
                    (item.payment_received)):
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_1_pre(cls):
        """return number of people on ticket class 1 (paid)"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if (
                (item.ticket_type == 3) and
                    (not 'CASHDESK' in item.email_confirm_code) and
                    (item.payment_received)):
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_green_pre(cls):
        """return number people on ticket class green mamba"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if (
                (item.ticket_type == 4) and
                    (not 'CASHDESK' in item.email_confirm_code) and
                    (item.payment_received)):
                _num = _num + item.num_tickets
        return _num

    # cashdesk
    @classmethod
    def get_num_class_2_cash(cls):
        """return number people on ticket class 2"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 1 and 'CASHDESK' in item.email_confirm_code:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_2_food_cash(cls):
        """return number people on ticket class 2 with foodstamp"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 2 and 'CASHDESK' in item.email_confirm_code:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_1_cash(cls):
        """return number people on ticket class 1"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 3 and 'CASHDESK' in item.email_confirm_code:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_class_green_cash(cls):
        """return number people on ticket class green mamba"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 4 and 'CASHDESK' in item.email_confirm_code:
                _num = _num + item.num_tickets
        return _num

    # totals
    @classmethod
    def get_sum_tickets_total(cls):
        """return sum of tickets (paid + unpaid)"""
        _all = DBSession.query(cls).all()
        _sum = 0
        for item in _all:
            _sum = _sum + item.the_total
        return _sum

    @classmethod
    def get_sum_tickets_unpaid(cls):
        """return sum of tickets not paid for/ no payment received yet"""
        _all = DBSession.query(cls).all()
        _sum = 0
        for item in _all:
            if not item.payment_received:
                _sum = _sum + item.the_total
        return _sum

    @classmethod
    def get_sum_tickets_paid(cls):
        """return sum of tickets already paid for"""
        _all = DBSession.query(cls).all()
        _sum = 0
        for item in _all:
            if item.payment_received:
                _sum = _sum + item.the_total
        return _sum

    @classmethod
    def get_sum_tickets_paid_desk(cls):
        """return sum of tickets issued at cashdesk"""
        _all = DBSession.query(cls).all()
        _sum = 0
        for item in _all:
            if 'CASHDESK' in item.email_confirm_code:
                _sum = _sum + item.the_total
        return _sum

    @classmethod
    def get_sum_tickets_preorder_cash(cls):
        """return sum of tickets preordered but paid only at cashdesk"""
        _all = DBSession.query(cls).all()
        _sum = 0
        for item in _all:
            if (
                (not 'CASHDESK' in item.email_confirm_code) and
                    (item.payment_received_date > datetime(
                        2014, 2, 14, 17, 30, 00, 000000)) and
                    (item.payment_received_date < datetime(
                        2014, 2, 14, 23, 30, 00, 000000))):
                _sum = _sum + item.the_total
        return _sum

    @classmethod
    def get_sum_tickets_new_cash(cls):
        """return sum of new tickets paid at cashdesk"""
        _all = DBSession.query(cls).all()
        _sum = 0
        for item in _all:
            if (
                ('CASHDESK' in item.email_confirm_code) and
                    (item.payment_received_date > datetime(
                        2014, 2, 14, 17, 30, 00, 000000)) and
                    (item.payment_received_date < datetime(
                        2014, 2, 14, 23, 30, 00, 000000))):
                _sum = _sum + item.the_total
        return _sum

    @classmethod
    def get_num_passengers_paid_checkedin(cls):
        """return number of paying passengers checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.payment_received and item.ticket_type is not 5:
                _num = _num + item.checked_persons
        return _num

    @classmethod
    def ticket_listing(cls, order_by, how_many=10, offset=0):
        #print("offset: %s" % offset)
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).all()[_offset:_how_many]
        #return q.order_by(order_by)[:how_many]
        return q

    @classmethod
    def check_password(cls, _id, password):
        member = cls.get_by_id(_id)
        return crypt.check(member.password, password)

    # this one is used by RequestWithUserAttribute
    @classmethod
    def check_user_or_None(cls, _id):
        """
        check whether a user by that username exists in the database.
        if yes, return that object, else None.
        returns None if username doesn't exist
        """
        login = cls.get_by_id(_id)  # is None if user not exists
        return login

Index('ticket_index', PartyTicket.tcodes, unique=True, mysql_length=255)
