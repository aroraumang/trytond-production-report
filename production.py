# -*- coding: utf-8 -*-
"""
    production.py

    :copyright: (c) 2014-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from dateutil import rrule, parser
from datetime import date, datetime, timedelta
from itertools import groupby
from openlabs_report_webkit import ReportWebkit

from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateAction, StateView, Button


__metaclass__ = PoolMeta
__all__ = [
    'ProductionReport', 'ProductionsReport', 'ProductionsReportWizardStart',
    'ProductionsReportWizard'
]


class ReportMixin(ReportWebkit):
    """
    Mixin Class to inherit from, for all HTML reports.
    """

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        Company = Pool().get('company.company')

        company = ''
        if Transaction().context.get('company'):
            company = Company(Transaction().context.get('company')).party.name
        options = {
            'margin-bottom': '0.50in',
            'margin-left': '0.50in',
            'margin-right': '0.50in',
            'margin-top': '0.50in',
            'footer-font-size': '8',
            'footer-left': company,
            'footer-line': '',
            'footer-right': '[page]/[toPage]',
            'footer-spacing': '5',
        }
        return super(ReportMixin, cls).wkhtml_to_pdf(
            data, options=options
        )


class ProductionReport(ReportMixin):
    """
    Production Report
    """
    __name__ = 'production.report'


class ProductionsReport(ReportMixin):
    """
    Productions Report
    """
    __name__ = 'report.productions'

    @classmethod
    def parse(cls, report, records, data, localcontext):
        Production = Pool().get('production')

        productions = Production.search([
            ('planned_date', '>=', data['start_date']),
            ('planned_date', '<=', data['end_date']),
            ('state', 'not in', ['request', 'cancel'])
        ])
        dates = [
            data['start_date'] + timedelta(days=d) for d in range(
                (data['end_date'] - data['start_date']).days + 1
            )
        ]

        # Dict object to hold productions with key as date and valeue
        # as list of productions on that day
        productions_by_date = dict.fromkeys(dates, [])

        # Group searched productions by date and for a dictionary out
        # of it
        productions_grouped_by_date = dict(
            (k,list(v)) for k,v in groupby(
                sorted(productions, key=lambda p: p.planned_date),
                key=lambda p: p.planned_date
            )
        )
        # Update the values in productions_by_date
        productions_by_date.update(productions_grouped_by_date)

        localcontext.update({
            'productions_by_date': productions_by_date,
            'dates': dates
        })
        return super(ProductionsReport, cls).parse(
            report, records, data, localcontext
        )


class ProductionsReportWizardStart(ModelView):
    'Generate Productions Report'
    __name__ = 'report.productions.wizard.start'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    @staticmethod
    def default_start_date():
        """
        Set default start date to the Monday of current week
        """
        today_ordinal = date.today().toordinal()

        # If today is Sunday, set default as last week's Monday
        if today_ordinal % 7 == 0:  # pragma: no cover
            today_ordinal -= 7
        return date.fromordinal(today_ordinal - (today_ordinal % 7) + 1)

    @staticmethod
    def default_end_date():
        """
        Set default end date to the Saturday of current week
        """
        today_ordinal = date.today().toordinal()

        # If today is Sunday, set default as last week's Saturday
        if today_ordinal % 7 == 0:  # pragma: no cover
            today_ordinal -= 7
        return date.fromordinal(today_ordinal - (today_ordinal % 7) + 6)


class ProductionsReportWizard(Wizard):
    'Generate Productions Report Wizard'
    __name__ = 'report.productions.wizard'

    start = StateView(
        'report.productions.wizard.start',
        'production_report.report_productions_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Generate', 'generate', 'tryton-ok', default=True),
        ]
    )
    generate = StateAction(
        'production_report.report_productions'
    )

    def do_generate(self, action):
        """
        Return report action and the data to pass to it
        """
        data = {
            'start_date': self.start.start_date,
            'end_date': self.start.end_date
        }
        return action, data

    def transition_generate(self):
        return 'end'
