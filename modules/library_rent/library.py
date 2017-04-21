# This file is part of Coog. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import datetime
from itertools import groupby

from trytond.model import ModelSQL, ModelView, Unique, Check, fields

from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Or, Bool, Equal
from library import *


__all__ = [
    'Book',
    'User',
    'Rent',
    ]

LIBRARY_RENT_LIMIT = 5
LIBRARY_LATE_LIMIT = 4


class Book():

    __metaclass__ = PoolMeta

    __name__ = 'library.book'

    # Basic Fields
    amount = fields.Integer('Amount', required=True)

    # Relational Fields
    renter = fields.Many2Many('library.rent', 'book', 'renter', 'Renter')

    rents = fields.One2Many('library.rent', 'book', 'Rents')

    left = fields.Function(
        fields.Integer('Left'),
        'get_left', searcher='search_left')

    available = fields.Function(fields.Integer('Available'),
        'get_available', searcher='search_available')

    # Setup
    @classmethod
    def __setup__(cls):
        super(Book, cls).__setup__()
        cls._error_messages.update({
                'bookrequire': 'Need more books',
                'bookamounterror': 'Amount should be at least set to 1',
                })
        t = cls.__table__()
        cls._sql_constraints += [
            ('code_unique', Unique(t, t.isbn), 'The code must be unique'),
            ('positive_integer', Check(t, t.amount > 0),
                'Positive integer amount required')]

    # Defaults values
    @staticmethod
    def default_amount():
        return 1

    # Dependence
    def get_left(self, name):
        amount = 0
        for rent in self.rents:
            if rent.rendered is None:
                amount += 1
        return self.amount - amount

    def get_available(self, name):
        return left > 0

    @classmethod
    def validate(cls, books):
        super(Book, cls).validate(books)

    @classmethod
    def search_left(cls, name, clause):
        Book = Pool().get('library.book')
        books = Book.search([])
        book_list = []
        if clause[1] == '=':
                book_list = [x.id for x in books
                    if x.get_left(name) == clause[2]]
        elif clause[1] == '!=':
                book_list = [x.id for x in books
                    if x.get_left(name) != clause[2]]
        return ['id', 'in', book_list]


class Rent(ModelSQL, ModelView):
    'Library Location'
    __name__ = 'library.rent'

    renter = fields.Many2One('party.party', 'Renter', ondelete='CASCADE',
        required=True, select=True)
    book = fields.Many2One('library.book', 'Book', ondelete='CASCADE',
        required=True, select=True, )

    rented = fields.Date('Rented')
    limit = fields.Function(
        fields.Date('Rent_limit'),
        'get_rent_limit')
    color = fields.Function(
        fields.Char('Color'),
        'get_color')
    rendered = fields.Date('Rendered')

    @classmethod
    def __setup__(cls):
        super(Rent, cls).__setup__()
        cls._error_messages.update({
                'nonerent': 'None rent selected',
                })
        cls._buttons.update({
                'button_library_rend': {
                    'invisible': Or(Bool(Eval('rendered')),
                        Eval('id') is None),
                    'icon': 'tryton-go-next',
                        }
                })

    @staticmethod
    def default_rented():
        return Pool().get('ir.date').today()

    def get_rent_limit(self, name=None):
        return self.rented + datetime.timedelta(days=LIBRARY_RENT_LIMIT)

    def get_color(self, name=None):
        return 'red' if ((self.rendered is None)
            and (Pool().get('ir.date').today() > self.limit)) else 'black'

    @classmethod
    def view_attributes(cls):
        return super(Rent, cls).view_attributes() + [
            ('/tree', 'colors', Eval('color')),
        ]

    @classmethod
    @ModelView.button_action('library_rent.library_rent_wizard')
    def button_library_rend(cls, users):
        pass

    @classmethod
    def validate(cls, rents):
        super(Rent, cls).validate(rents)

        def group_(rent):
            return rent.book

        rents = sorted(rents, key=group_)

        for book, rents_per_book in groupby(rents, group_):
            rents_per_book = list(rents_per_book)
            if book.left < 0:
                book.raise_user_error('bookrequire')

    @classmethod
    @ModelView.button
    def render(cls, rents):
        pool = Pool()
        Date = pool.get('ir.date')
        cls.write(rents, {'rendered': Date.today(),
            })


class User(ModelSQL, ModelView):
    "User"
    __name__ = 'party.party'
    name = fields.Char('Name')

    rented_books = fields.Many2Many('library.rent', 'renter', 'book', 'Books')

    rents = fields.One2Many('library.rent', 'book', 'Rents')

    late = fields.Function(fields.Integer('Late'), 'get_late',
        searcher="search_late")

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._buttons.update({
                'button_library_rent_user': {
                    'invisible': Bool(Equal(Eval('late', 0), LIBRARY_LATE_LIMIT
                        )),
                    'icon': 'tryton-go-next',
                    }
                })

    @staticmethod
    def default_state():
        return('permitted')

    def get_late(self, name=None):
        amount = 0
        for rent in self.rents:
            if rent.rendered is not None and rent.rendered > rent.limit:
                amount += 1

        return amount

    @classmethod
    @ModelView.button_action('library_rent.library_rent_user_wizard')
    def button_library_rent_user(cls, users):
        pass

    @classmethod
    def search_late(cls, name, clause):
        User = Pool().get('party.party')
        users = User.search([])
        user_list = []
        if clause[1] == '=':
                user_list = [x.id for x in users
                    if x.get_late(name) == clause[2]]
        elif clause[1] == '!=':
                user_list = [x.id for x in users
                    if x.get_late(name) != clause[2]]

        return ['id', 'in', user_list]
