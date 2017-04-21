# This file is part of Coog. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.wizard import StateTransition, StateView, Button, StateAction
from trytond.wizard import Wizard
from trytond.transaction import Transaction

from trytond.model import ModelView, fields

from trytond.modules.library_rent import *

__all__ = [
    'PrintLibraryReport',
    'PrintLibraryReportStart',
    'LibraryRenderWiz',
    'LibraryRendSart',
    'UserDoRent',
    'UserDoRentStart',
    ]


class PrintLibraryReportStart(ModelView):
    'Print Library Report'
    __name__ = 'library.print_report.start'


class PrintLibraryReport(Wizard):
    'Print Library Report'
    __name__ = 'library.print_report'

    start = StateView(
        'library.print_report.start', 'library_rent.print_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Print', 'print_', 'tryton-print', default=True),
            ]
        )
    print_ = StateAction('library.book')

    def do_print(self, action):
        data = {
            'library': self.start.book.id,
            }
        return action, data

    def transition_print(self):
        return 'end'


class UserDoRentStart(ModelView):
    'User do Rent'
    __name__ = 'library.user_do_rent.start'

    user = fields.Many2One('party.party', 'User', required=True, readonly=True)
    name = fields.Char('Name', readonly=True)
    book = fields.Many2Many('library.rent', 'renter', 'book', 'Book',
        required=True, domain=[('left', '!=', 0)])


class UserDoRent(Wizard):
    'User do Rent'
    __name__ = 'library.user_do_rent'

    start = StateView(
        'library.user_do_rent.start', 'library_rent.library_rent_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Rent', 'do_rent', 'tryton-ok', default=True),
            ])
    do_rent = StateTransition()

    def default_start(self, name):
        assert Transaction().context.get('active_model') == 'party.party'
        user = Pool().get('party.party')(Transaction().context.get('active_id'
                ))
        return{
            'user': user.id,
            'name': user.name,
        }

    def transition_do_rent(self):
        for book in self.start.book:
            new_rent = Rent(renter=self.start.user, book=book)
            new_rent.save()
        return 'end'


class LibraryRendSart(ModelView):
    'Rend Rent'
    __name__ = 'library.rend.start'

    rent = fields.One2Many('library.rent', None, 'Rent', required=True,
        readonly=True)


class LibraryRenderWiz(Wizard):
    'Rent Rent'
    __name__ = 'library.rend_do'

    start = StateView(
        'library.rend.start', 'library_rent.library_rend_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Rent', 'do_rent', 'tryton-ok', default=True)

            ])

    do_rent = StateTransition()

    def default_start(self, name):
        assert Transaction().context.get('active_model') == 'library.rent'
        rents = Transaction().context.get('active_ids')
        print(Transaction().context.get('active_ids'))
        return{
            'rent': [x for x in rents],

        }

    def transition_do_rent(self):
        rents = self.start.rent
        for rent in rents:
            rent.render([rent])
        return 'end'
