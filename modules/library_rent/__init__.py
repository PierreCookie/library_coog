# This file is part of Coog. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from .library import *
from .wizard import *

from trytond.pool import Pool


def register():
    Pool.register(
        User,
        Book,
        Rent,
        PrintLibraryReportStart,
        LibraryRendSart,
        UserDoRentStart,
        module='library_rent', type_='model'
    )
    Pool.register(
        PrintLibraryReport,
        LibraryRenderWiz,
        UserDoRent,
        module='library_rent', type_='wizard')
