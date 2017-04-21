# This file is part of Coog. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import Pool

from .library import Book


def register():
    Pool.register(
        Book,
        module='library', type_='model'
    )
