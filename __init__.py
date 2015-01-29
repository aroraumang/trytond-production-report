# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from production import ProductionReport, ProductionsReport, \
    ProductionsReportWizardStart, ProductionsReportWizard


def register():
    Pool.register(
        ProductionReport,
        ProductionsReport,
        module='production_report', type_='report'
    )
    Pool.register(
        ProductionsReportWizardStart,
        module='production_report', type_='model'
    )
    Pool.register(
        ProductionsReportWizard,
        module='production_report', type_='wizard'
    )
