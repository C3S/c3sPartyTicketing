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
    def get_by_login(cls, login):
        #dbSession = DBSession()
        return DBSession.query(cls).filter(cls.login == login).first()

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
    ticket_type = Column(Integer)
    the_total = Column(Integer)
    date_of_submission = Column(DateTime(), nullable=False)
    payment_received = Column(Boolean, default=False)
    payment_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    payment_confirmed = Column(Boolean, default=False)
    payment_confirmed_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    user_comment = Column(Unicode(255))
    accountant_comment = Column(Unicode(255))

    def __init__(self, firstname, lastname, email, password,
                 locale,
                 email_is_confirmed, email_confirm_code,
                 date_of_submission,
                 num_tickets,
                 ticket_type,
                 the_total,
                 user_comment,
                 ):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.num_tickets = num_tickets
        self.ticket_type = ticket_type
        self.the_total = the_total
        self.password = password
        self.last_password_change = datetime.now()
        self.locale = locale
        self.email_is_confirmed = email_is_confirmed
        self.email_confirm_code = email_confirm_code
        self.date_of_submission = datetime.now()
        self.signature_received = False
        self.payment_received = False
        self.user_comment = user_comment

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

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

    @classmethod
    def get_by_tcode(cls, tcode):
        """
        find a member by ticket code
        """
        return DBSession.query(cls).filter(
            cls.email_confirm_code == tcode).first()

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

    @classmethod
    def check_for_existing_ticket_code(cls, tcode):
        """
        check if a code is already present
        """
        check = DBSession.query(cls).filter(
            cls.tcode == tcode).first()
        if check:  # pragma: no cover
            return True
        else:
            return False

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
        """return number of members (by counting rows in table)"""
        return DBSession.query(cls).count()

    @classmethod
    def num_passengers(cls):
        """return number of people already checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
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
