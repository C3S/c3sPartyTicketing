# -*- coding: utf-8  -*-
"""
This module holds the Database Model for c3sPartyTicketing.

For each data object used there is a class below.
"""

# import transaction
# import cryptacular.bcrypt
from datetime import (
    # date,
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
    Float,
    Boolean,
    DateTime,
    # Date,
    Unicode,
    or_,
)
# from sqlalchemy.exc import (
#    IntegrityError,
#    OperationalError,
#    InvalidRequestError
# )
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
        # print('=== get_kasse_group:' + str(kasse_group))
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

    # @property
    # def __acl__(self):
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
        staffer = cls.get_by_login(login)
        # if staffer is None:  # ?
        #    return False
        # if not staffer:  # ?
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
    """
    The ticket database entries.
    """
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    """technical id; number of database entry in table"""
    # person info
    token = Column(Text)
    """a unique token"""
    firstname = Column(Text)
    """the first name"""
    lastname = Column(Text)
    """the last name"""
    email = Column(Unicode(255))
    """email address"""
    membership_type = Column(Unicode(255), unique=False)
    """membership type"""
    is_legalentity = Column(Boolean, default=False)
    """flag for legal entities"""
    _password = Column('password', Unicode(60))
    """a password hash"""
    last_password_change = Column(
        DateTime,
        default=func.current_timestamp())
    locale = Column(Unicode(255))
    email_is_confirmed = Column(Boolean, default=False)
    email_confirm_code = Column(Unicode(255), unique=True)
    # ticket info
    tcodes = Column(Unicode(255), unique=True)
    num_tickets = Column(Integer, default=1)
    checked_persons = Column(Integer, default=0)
    checked_gv = Column(Boolean, default=False)
    checked_gv_time = Column(
        DateTime(), default=datetime(1970, 1, 1))
    checked_bc = Column(Boolean, default=False)
    checked_bc_time = Column(
        DateTime(), default=datetime(1970, 1, 1))
    received_extra1 = Column(Boolean, default=False)  # brief
    received_extra1_time = Column(
        DateTime(), default=datetime(1970, 1, 1))
    received_extra2 = Column(Boolean, default=False)  # tshirt
    received_extra2_time = Column(
        DateTime(), default=datetime(1970, 1, 1))
    received_extra3 = Column(Boolean, default=False)  # unbenutzt
    received_extra3_time = Column(
        DateTime(), default=datetime(1970, 1, 1))
    ticket_gv_attendance = Column(Integer)
    ticket_bc_attendance = Column(Boolean, default=False)
    ticket_bc_buffet = Column(Boolean, default=False)
    ticket_tshirt = Column(Boolean, default=False)
    ticket_tshirt_type = Column(Integer)
    ticket_tshirt_size = Column(Integer)
    ticket_all = Column(Boolean, default=False)
    ticket_support = Column(Boolean, default=False)
    ticket_support_x = Column(Boolean, default=False)
    ticket_support_xl = Column(Boolean, default=False)
    support = Column(Float)
    discount = Column(Float)
    the_total = Column(Float)
    # representation
    rep_firstname = Column(Text, default='')
    rep_lastname = Column(Text, default='')
    rep_street = Column(Text, default='')
    rep_zip = Column(Text, default='')
    rep_city = Column(Text, default='')
    rep_country = Column(Text, default='')
    rep_type = Column(Integer)
    rep_email = Column(Text, default='')
    represents_id1 = Column(Integer)
    represents_id2 = Column(Integer)
    # guestlist
    guestlist = Column(Boolean, default=False)
    guestlist_gv = Column(Unicode(255), unique=False)
    guestlist_bc = Column(Unicode(255), unique=False)
    # meta
    date_of_submission = Column(DateTime(), nullable=False)
    payment_received = Column(Boolean, default=False)
    payment_received_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    ticketmail_sent = Column(Boolean, default=False)
    ticketmail_sent_date = Column(
        DateTime(), default=datetime(1970, 1, 1))
    user_comment = Column(Unicode(255))
    accountant_comment = Column(Unicode(255))
    staff_comment = Column(Text, default='')
    cashiers_comment = Column(Text, default='')

    def __init__(self, token, firstname, lastname, email, password,
                 locale,
                 email_is_confirmed, email_confirm_code,
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
                 payment_received=False
                 ):
        self.token = token
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.num_tickets = num_tickets
        self.ticket_gv_attendance = ticket_gv_attendance
        self.ticket_bc_attendance = ticket_bc_attendance
        self.ticket_bc_buffet = ticket_bc_buffet
        self.ticket_tshirt = ticket_tshirt
        self.ticket_tshirt_type = ticket_tshirt_type
        self.ticket_tshirt_size = ticket_tshirt_size
        self.ticket_all = ticket_all
        self.ticket_support = ticket_support
        self.ticket_support_x = ticket_support_x
        self.ticket_support_xl = ticket_support_xl
        self.support = support
        self.discount = discount
        self.the_total = the_total
        self.rep_firstname = rep_firstname
        self.rep_lastname = rep_lastname
        self.rep_street = rep_street
        self.rep_zip = rep_zip
        self.rep_city = rep_city
        self.rep_country = rep_country
        self.rep_type = rep_type
        self.guestlist = guestlist
        self.password = password
        self.last_password_change = datetime.now()
        self.locale = locale
        self.email_is_confirmed = email_is_confirmed
        self.email_confirm_code = email_confirm_code
        self.date_of_submission = datetime.now()
        self.payment_received = payment_received
        self.user_comment = user_comment

    @classmethod
    def get_by_code(cls, email_confirm_code):
        """
        find a ticket by email confirmation code

        this is needed when a user returns from reading her email
        and clicking on a link containing the confirmation code.
        as the code is unique, one record is returned.
        """
        return DBSession.query(cls).filter(
            cls.email_confirm_code == email_confirm_code).first()

    @classmethod
    def get_by_token(cls, token):
        """
        find a ticket by token

        this is needed when a user returns from reading her email
        and clicking on a link containing the link with a token.
        as the code is unique, one record is returned.
        """
        return DBSession.query(cls).filter(
            cls.token == token).first()

    @classmethod
    def has_token(cls, token):
        """
        check, if a ticket with given token already exists

        this is needed to redirect to a readonly form, if a user
        has already submitted the form
        """
        return DBSession.query(cls).filter(
            cls.token == token).count()

    # @classmethod
    # def get_by_tcode(cls, tcode):
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
        # print("codes before returning from classmethod: %s" % codes)
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
    def delete_by_token(cls, _token):
        """return one member by id"""
        return DBSession.query(cls).filter(cls.token == _token).delete()

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
    # @classmethod
    # def get_num_member(cls):
    #     """return number of all members with database entry"""
    #     return DBSession.query(cls).filter(
    #         cls.membership_type != u'nonmember').count()

    # @classmethod
    # def get_num_nonmember(cls):
    #     """return number of non members with database entry"""
    #     return DBSession.query(cls).filter(
    #         cls.membership_type == u'nonmember').count()

    @classmethod
    def get_num_normal(cls):
        """return number of normal members w/ ticket"""
        return DBSession.query(cls).filter(
            cls.membership_type == u'normal').count()

    @classmethod
    def get_num_investing(cls):
        """return number of investing members w/ ticket"""
        return DBSession.query(cls).filter(
            cls.membership_type == u'investing').count()

    @classmethod
    def get_num_normal_checked(cls):
        """return number of hobos checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if (item.membership_type == u'investing'):
                _num = _num + item.checked_persons
        return _num

    @classmethod
    def get_num_investing_checked(cls):
        """return number of hobos checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if (item.membership_type == u'investing'):
                _num = _num + item.checked_persons
        return _num

    # totals
    @classmethod
    def get_num_hobos(cls):
        """return number of hobos"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.guestlist:
                _num = _num + item.num_tickets
        return _num

    @classmethod
    def get_num_hobos_checked(cls):
        """return number of hobos checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            if item.ticket_type == 5:
                # (
                # (item.ticket_type == 5) and
                #    (item.checked_persons is not item.num_tickets)):
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
                    ('CASHDESK' not in item.email_confirm_code) and
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
                    ('CASHDESK' not in item.email_confirm_code) and
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
                    ('CASHDESK' not in item.email_confirm_code) and
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
                    ('CASHDESK' not in item.email_confirm_code) and
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
                ('CASHDESK' not in item.email_confirm_code) and
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
        # print("offset: %s" % offset)
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).all()[_offset:_how_many]
        # return q.order_by(order_by)[:how_many]
        return q

    @classmethod
    def ticket_listing_ga(cls, order_by, how_many=10, offset=0):
        # print("offset: %s" % offset)
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).filter(
            or_(
                cls.ticket_gv_attendance == 1,
                cls.ticket_gv_attendance == 2,
            )
        ).all()[_offset:_how_many]
        # return q.order_by(order_by)[:how_many]
        return q

    @classmethod
    def ticket_listing_bc(cls, order_by, how_many=10, offset=0):
        # print("offset: %s" % offset)
        _how_many = int(offset) + int(how_many)
        _offset = int(offset)
        q = DBSession.query(cls).filter(
            or_(
                cls.ticket_bc_attendance == 1,
                cls.ticket_bc_attendance == 2,
            )
        ).all()[_offset:_how_many]
        # return q.order_by(order_by)[:how_many]
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

    # stats
    @classmethod
    def get_stats_cfg(cls):
        return {
            # templates
            'tpl': {
                # template for membership_type categories
                'mt': {
                    'total': 0,
                    'member': 0,
                    'normal': 0,
                    'investing': 0,
                    'nonmember': 0,
                    'unknown': 0,
                },
                # template for tshirts
                'tshirts': {
                    'total': 0,
                    'female': {
                        'S': 0,
                        'M': 0,
                        'L': 0,
                        'XL': 0,
                        'XXL': 0,
                        'XXXL': 0,
                    },
                    'male': {
                        'S': 0,
                        'M': 0,
                        'L': 0,
                        'XL': 0,
                        'XXL': 0,
                        'XXXL': 0,
                    },
                }
            },
            # mappings from db values to dict key in stats
            # XXX: centralize mappings
            'map': {
                # membership_type
                'mt': {
                    'normal': 'normal',
                    'investing': 'investing',
                    'nonmember': 'nonmember',
                    None: 'unknown',
                },
                # ticket_ga_attendance
                'gv': {
                    0: 'unknown',
                    1: 'participating',
                    2: 'represented',
                    3: 'cancelled',
                    None: 'unknown',
                },
                # ticket_bc_attendance
                'bc': {
                    True: 'participating',
                    False: 'cancelled',
                },
                # ticket_tshirt_type
                'tt': {
                    'f': 'female',
                    'm': 'male',
                },
            },
            # events
            'events': ('gv', 'bc'),
            # dict keys of membership types in stats for the total sum
            'mt_total': (u'normal', u'investing', u'nonmember', u'unknown'),
            # valid membership types in db
            'mt_valid': (u'normal', u'investing', u'nonmember'),
            # membership types in db, which constitute the member sum
            'mt_member': (u'normal', u'investing'),
            # testing values in db
            'dataprovider': {
                'membership_type': (u'normal', u'investing', None),
                'ticket_gv_attendance': (1, 2, 3, None),
                'ticket_bc_attendance': (True, False),
                'ticket_bc_buffet': (True, False),
                'ticket_tshirt': (True, False),
                'ticket_tshirt_type': (u'm', u'f'),
                'ticket_tshirt_size': (
                    u'S', u'M', u'L', u'XL', u'XXL', u'XXXL'
                ),
            }
        }

    @classmethod
    def get_stats_general(cls):
        """return general statistics"""
        _tpl = cls.get_stats_cfg()
        _stats = {
            'datasets': _tpl['tpl']['mt'].copy()
        }
        _all = DBSession.query(cls).all()
        for item in _all:
            _stats['datasets']['total'] += 1
            mt = item.membership_type
            if(mt in _tpl['mt_valid']):
                _stats['datasets'][mt] += 1
                if(mt in _tpl['mt_member']):
                    _stats['datasets']['member'] += 1
            else:
                _stats['datasets']['unknown'] += 1
        return _stats

    @classmethod
    def get_stats_events(cls):
        """return statistics of events"""
        _tpl = cls.get_stats_cfg()
        _stats = {
            'gv': {
                'participating': _tpl['tpl']['mt'].copy(),
                'represented': _tpl['tpl']['mt'].copy(),
                'cancelled': _tpl['tpl']['mt'].copy(),
                'unknown': _tpl['tpl']['mt'].copy(),
            },
            'bc': {
                'participating': _tpl['tpl']['mt'].copy(),
                'cancelled': _tpl['tpl']['mt'].copy(),
                'buffet': _tpl['tpl']['mt'].copy(),
            }
        }
        _all = DBSession.query(cls).all()
        for item in _all:
            mt = item.membership_type
            map_gv = _tpl['map']['gv'][item.ticket_gv_attendance]
            map_bc = _tpl['map']['bc'][item.ticket_bc_attendance]
            # general assembly attendance
            if(mt in _tpl['mt_member']):
                _stats['gv'][map_gv]['total'] += 1
                _stats['gv'][map_gv][mt] += 1
                _stats['gv'][map_gv]['member'] += 1
            # barcamp attendace
            _stats['bc'][map_bc]['total'] += 1
            if(mt in _tpl['mt_valid']):
                _stats['bc'][map_bc][mt] += 1
                if(mt in _tpl['mt_member']):
                    _stats['bc'][map_bc]['member'] += 1
            else:
                _stats['bc'][map_bc]['unknown'] += 1
            # barcamp buffet
            if(item.ticket_bc_buffet):
                _stats['bc']['buffet']['total'] += 1
                if(mt in _tpl['mt_valid']):
                    _stats['bc']['buffet'][mt] += 1
                    if(mt in _tpl['mt_member']):
                        _stats['bc']['buffet']['member'] += 1
                else:
                    _stats['bc']['buffet']['unknown'] += 1
        return _stats

    @classmethod
    def get_stats_extras(cls):
        """return statistics of extras"""
        _tpl = cls.get_stats_cfg()
        _stats = {
            'tshirts': _tpl['tpl']['tshirts']
        }
        _all = DBSession.query(cls).all()
        for item in _all:
            if(item.ticket_tshirt):
                map_tt = _tpl['map']['tt'][item.ticket_tshirt_type]
                _stats['tshirts']['total'] += 1
                _stats['tshirts'][map_tt][item.ticket_tshirt_size] += 1
        return _stats

    @classmethod
    def stats_cashiers(cls):
        """return stats of people attending / checked in"""
        _all = DBSession.query(cls).all()
        _data = {
            'bc': {
                'checkedin': {
                    'all': 0,
                    'helper': 0,
                    'guest': 0,
                    'specialguest': 0,
                    'press': 0,
                },
                'expected': {
                    'all': 0,
                    'helper': 0,
                    'guest': 0,
                    'specialguest': 0,
                    'press': 0,
                },
            },
            'gv': {
                'checkedin': {
                    'all': 0,
                    'helper': 0,
                    'guest': 0,
                    'specialguest': 0,
                    'press': 0,
                    'representative': 0,
                },
                'expected': {
                    'all': 0,
                    'helper': 0,
                    'guest': 0,
                    'specialguest': 0,
                    'press': 0,
                    'representative': 0,
                },
            }
        }
        for item in _all:
            if item.ticket_bc_attendance:
                if item.checked_bc:
                    _data['bc']['checkedin']['all'] += 1
                    if item.guestlist_bc == 'helper':
                        _data['bc']['checkedin']['helper'] += 1
                    if item.guestlist_bc == 'guest':
                        _data['bc']['checkedin']['guest'] += 1
                    if item.guestlist_bc == 'specialguest':
                        _data['bc']['checkedin']['specialguest'] += 1
                    if item.guestlist_bc == 'press':
                        _data['bc']['checkedin']['press'] += 1
                else:
                    _data['bc']['expected']['all'] += 1
                    if item.guestlist_bc == 'helper':
                        _data['bc']['expected']['helper'] += 1
                    if item.guestlist_bc == 'guest':
                        _data['bc']['expected']['guest'] += 1
                    if item.guestlist_bc == 'specialguest':
                        _data['bc']['expected']['specialguest'] += 1
                    if item.guestlist_bc == 'press':
                        _data['bc']['expected']['press'] += 1
            if item.ticket_gv_attendance == 1:
                if item.checked_bc:
                    _data['gv']['checkedin']['all'] += 1
                    if item.guestlist_gv == 'helper':
                        _data['gv']['checkedin']['helper'] += 1
                    if item.guestlist_gv == 'guest':
                        _data['gv']['checkedin']['guest'] += 1
                    if item.guestlist_gv == 'specialguest':
                        _data['gv']['checkedin']['specialguest'] += 1
                    if item.guestlist_gv == 'press':
                        _data['gv']['checkedin']['press'] += 1
                    if item.guestlist_gv == 'representative':
                        _data['gv']['checkedin']['representative'] += 1
                else:
                    _data['gv']['expected']['all'] += 1
                    if item.guestlist_gv == 'helper':
                        _data['gv']['expected']['helper'] += 1
                    if item.guestlist_gv == 'guest':
                        _data['gv']['expected']['guest'] += 1
                    if item.guestlist_gv == 'specialguest':
                        _data['gv']['expected']['specialguest'] += 1
                    if item.guestlist_gv == 'press':
                        _data['gv']['expected']['press'] += 1
                    if item.guestlist_gv == 'representative':
                        _data['gv']['expected']['representative'] += 1
        return _data

    @classmethod
    def num_barcamp_checkdin(cls):
        """return number of people already checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            _num = _num + item.checked_persons
        return _num

    @classmethod
    def num_generalassembly_attending(cls):
        """return number of people already checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            _num = _num + item.checked_persons
        return _num

    @classmethod
    def num_generalassembly_checkdin(cls):
        """return number of people already checked in"""
        _all = DBSession.query(cls).all()
        _num = 0
        for item in _all:
            _num = _num + item.checked_persons
        return _num

Index('ticket_index', PartyTicket.tcodes, unique=True, mysql_length=255)
