# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright Camptocamp SA 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from collections import defaultdict
from datetime import datetime

from openerp.modules.registry import RegistryManager
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
from .common_partner_reports import CommonPartnersReportHeaderWebkit
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class PartnerInvoicedWebkit(report_sxw.rml_parse,
                            CommonPartnersReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(PartnerInvoicedWebkit, self).__init__(
            cursor, uid, name, context=context)
        self.pool = RegistryManager.get(self.cr.dbname)
        self.cursor = self.cr
        
        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join(
            (_('PARTNER INVOICED'), company.name, company.currency_id.name))

        footer_date_time = self.formatLang(
            str(datetime.today()), date_time=True)

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('Partner Invoiced'),
            'filter_form': self._get_filter,
            'display_only_total': self._get_display_only_total,
            'display_target_move': self._get_display_target_move,
            'accounts': self._get_accounts_br,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join(
                    (_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_display_only_total(self, data):
        val = self._get_form_param('display_only_total', data)
        return val

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a ledger_lines attribute on each browse record that will
           be used by mako template"""
        lang = self.localcontext.get('lang')
        lang_ctx = lang and {'lang': lang} or {}
        new_ids = data['form']['chart_account_id']
        main_filter = self._get_form_param('filter', data, default='filter_no')
        target_move = self._get_form_param(
            'target_move', data, default='posted')
        start_date = self._get_form_param('date_from', data)
        stop_date = self._get_form_param('date_to', data)
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        fiscalyear = self.get_fiscalyear_br(data)
        journal_ids = self._get_form_param('journal_ids', data)
        account_ids = self._get_form_param('account_ids', data)
        chart_account = self._get_chart_account_id_br(data)

        if main_filter == 'filter_no' and fiscalyear:
            start_period = self.get_first_fiscalyear_period(fiscalyear)
            stop_period = self.get_last_fiscalyear_period(fiscalyear)

        accounts = []
        account_obj = self.pool['account.account']
        if account_ids:
            for account_id in account_obj.browse(
                    self.cr, self.uid, account_ids):
                if account_id.type != 'view':
                    accounts.append(account_id.id)
                if account_id.type == 'view':
                    accounts += account_obj.search(self.cr, self.uid, [(
                        'parent_id', '=', account_id.id)])

        if not accounts:
            raise osv.except_osv(_('Error'), _('No accounts to print.'))

        if main_filter == 'filter_date':
            start = start_date
            stop = stop_date
        else:
            start = start_period
            stop = stop_period

        ledger_lines = self._compute_partner_ledger_lines(
            accounts, main_filter, target_move, start, stop, journal_ids)
        object_ids = []
        ledger_lines_dict = {}
        for account in self.pool.get('account.account').browse(
                self.cursor, self.uid, accounts):
            ledger_lines_dict[account.id] = ledger_lines.get(
                account.id, {})
            if len(ledger_lines_dict[account.id]) > 0:
                partner_id = ledger_lines.get(
                    account.id, {})[account.id][0]['partner_id'][0]
                partner = self.pool['res.partner'].browse(
                    self.cr, self.uid, partner_id)
                ledger_lines_dict[account.id]['vat'] = partner.vat
                ledger_lines_dict[account.id]['fiscalcode'] = \
                    partner.fiscalcode
                object_ids.append(account.id)
        if object_ids:
            objects = self.pool['account.account'].browse(
                self.cursor, self.uid, object_ids)

        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'start_date': start_date,
            'stop_date': stop_date,
            'start_period': start_period,
            'stop_period': stop_period,
            'account_ids': account_ids,
            'journal_ids': journal_ids,
            'chart_account': chart_account,
            'ledger_lines': ledger_lines_dict,
        })

        return super(PartnerInvoicedWebkit, self).set_context(
            objects, data, new_ids, report_type=report_type)

    def _compute_partner_ledger_lines(self, accounts_ids, main_filter,
                                      target_move, start, stop, journal_ids):
        res = defaultdict(dict)
        filter_from = False
        if main_filter in ('filter_period', 'filter_no'):
            filter_from = 'period'
        elif main_filter == 'filter_date':
            filter_from = 'date'
        for acc_id in accounts_ids:
            account_invoice_ids = self._get_account_invoice_ids(
                filter_from, acc_id, start, stop, target_move, journal_ids)
            if not account_invoice_ids:
                continue
            invoices_data = self.pool['account.invoice'].read(
                self.cr, self.uid, account_invoice_ids[acc_id],
                ['amount_untaxed_signed', 'internal_number', 'date_invoice',
                 'partner_id'])
            res[acc_id][acc_id] = invoices_data
        return res

    def _get_query_params_from_periods(
            self, period_start, period_stop, mode='exclude_opening'):
        """
        Build the part of the sql "where clause" which filters on the selected
        periods.

        :param browse_record period_start: first period of the report to print
        :param browse_record period_stop: last period of the report to print
        :param str mode: deprecated
        """
        # we do not want opening period so we exclude opening
        periods = self.pool.get('account.period').build_ctx_periods(
                self.cr, self.uid, period_start.id, period_stop.id)
        if not periods:
            return []

        periods = self.exclude_opening_periods(periods)

        search_params = {'period_ids': tuple(periods),
                         'date_stop': period_stop.date_stop}

        sql_conditions = "  AND account_invoice.period_id in %(period_ids)s"

        return sql_conditions, search_params

    def _get_query_params_from_dates(self, date_start, date_stop, **args):
        """
        Build the part of the sql where clause based on the dates to print.

        :param str date_start: start date of the report to print
        :param str date_stop: end date of the report to print
        """

        periods = self._get_opening_periods()
        if not periods:
            periods = (-1,)

        search_params = {'period_ids': tuple(periods),
                         'date_start': date_start,
                         'date_stop': date_stop}

        sql_conditions = \
            "  AND account_invoice.period_id not in %(period_ids)s" \
            "  AND account_invoice.date_invoice between date(%(date_start)s)" \
            " and date((%(date_stop)s))"

        return sql_conditions, search_params

    def _get_account_invoice_ids(
            self, filter_from, account_id, start, stop, target_move,
            journal_ids):
        final_res = defaultdict(list)

        sql_select = "SELECT account_invoice.id, account_invoice.account_id " \
                     "FROM account_invoice"
        sql_joins = ''
        sql_where = " WHERE account_invoice.account_id = %(account_ids)s " \
                    " AND account_invoice.state in %(target_invoice)s "

        sql_conditions, search_params = getattr(
            self, '_get_query_params_from_'+filter_from+'s')(start, stop)

        sql_where += sql_conditions

        if journal_ids:
            sql_joins += " INNER JOIN account_journal ON " \
                         "account_invoice.journal_id = account_journal.id"
            sql_where += " AND account_journal.id in %(journal_ids)s"
            search_params.update({'journal_ids': tuple(journal_ids),})

        target_invoice = ['open', 'paid']
        if target_move == 'all':
            target_invoice += ['draft']

        search_params.update({
            'account_ids': account_id,
            'target_invoice': tuple(target_invoice),
        })

        sql = ' '.join((sql_select, sql_joins, sql_where,
                        ' ORDER BY date_invoice ASC '))
        self.cursor.execute(sql, search_params)
        res = self.cursor.dictfetchall()
        if res:
            for row in res:
                final_res[row['account_id']].append(row['id'])
        return final_res


HeaderFooterTextWebKitParser(
    'report.account.account_report_partner_invoiced_webkit',
    'account.account',
    'addons/account_financial_report_webkit/report/templates/\
        account_report_partner_invoiced.mako',
    parser=PartnerInvoicedWebkit)
