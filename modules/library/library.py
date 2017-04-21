# This file is part of Coog. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields

# list of alls classes in the file
__all__ = [
    'Book',
    ]


class Book(ModelSQL, ModelView):
    # description
    'Book'

    # Internal class name. ALways used as a reference inside Tryton
    # default: '<module name>.<class name>' on Tryton
    # becomes '<module name> <class name>' in the database

    __name__ = 'library.book'

    title = fields.Char('Title', required=True, select=True)
    isbn = fields.Char('ISBN')
    subject = fields.Selection([
            ('history', 'History'),
            ('sf', 'SF'),
            ('thriller', 'Thriller'),
            ('drama', 'Drama'),
            ('cop', 'Cop'),
            ],
            'Subject',)
    abstract = fields.Text('Abstract')

    def get_rec_name(self, name):
        return self.title
