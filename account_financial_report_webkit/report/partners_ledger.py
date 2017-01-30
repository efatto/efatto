# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
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

from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
from .common_partner_reports import CommonPartnersReportHeaderWebkit
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class PartnersLedgerWebkit(report_sxw.rml_parse,
                           CommonPartnersReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(PartnersLedgerWebkit, self).__init__(
            cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('PARTNER LEDGER'),
                                        company.name,
                                        company.currency_id.name))

        footer_date_time = self.formatLang(
            str(datetime.today()), date_time=True)

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('Partner Ledger'),
            'display_account_raw': self._get_display_account_raw,
            'filter_form': self._get_filter,
            'target_move': self._get_target_move,
            'initial_balance': self._get_initial_balance,
            'amount_currency': self._get_amount_currency,
            'display_partner_account': self._get_display_partner_account,
            'display_target_move': self._get_display_target_move,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right',
                 ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_initial_balance_mode(self, start_period):
        """ Force computing of initial balance for the partner ledger,
        because we cannot use the entries generated by
        OpenERP in the opening period.

        OpenERP allows to reconcile move lines between different partners,
        so the generated entries in the opening period are unreliable.
        """
        return 'initial_balance'

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a ledger_lines attribute on each browse record that will
           be used by mako template"""
        new_ids = data['form']['chart_account_id']

        # account partner memoizer
        # Reading form
        main_filter = self._get_form_param('filter', data, default='filter_no')
        target_move = self._get_form_param('target_move', data, default='all')
        start_date = self._get_form_param('date_from', data)
        stop_date = self._get_form_param('date_to', data)
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        fiscalyear = self.get_fiscalyear_br(data)
        partner_ids = self._get_form_param('partner_ids', data)
        result_selection = self._get_form_param('result_selection', data)
        chart_account = self._get_chart_account_id_br(data)
        group_invoice_payments = self._get_form_param(
            'group_invoice_payments', data)

        if main_filter == 'filter_no' and fiscalyear:
            start_period = self.get_first_fiscalyear_period(fiscalyear)
            stop_period = self.get_last_fiscalyear_period(fiscalyear)

        # Retrieving accounts
        filter_type = ('payable', 'receivable')
        if result_selection == 'customer':
            filter_type = ('receivable',)
        if result_selection == 'supplier':
            filter_type = ('payable',)

        accounts = self.get_all_accounts(new_ids, exclude_type=['view'],
                                         only_type=filter_type)

        if not accounts:
            raise osv.except_osv(_('Error'), _('No accounts to print.'))

        if main_filter == 'filter_date':
            start = start_date
            stop = stop_date
        else:
            start = start_period
            stop = stop_period

        # when the opening period is included in the selected range of periods
        # and the opening period contains move lines, we must not compute the
        # initial balance from previous periods but only display the move lines
        # of the opening period we identify them as:
        #  - 'initial_balance' means compute the sums of move lines from
        #    previous periods
        #  - 'opening_balance' means display the move lines of the opening
        #    period
        init_balance = main_filter in ('filter_no', 'filter_period')
        initial_balance_mode = init_balance and self._get_initial_balance_mode(
            start) or False

        initial_balance_lines = {}
        if initial_balance_mode == 'initial_balance':
            initial_balance_lines = self._compute_partners_initial_balances(
                accounts, start_period, partner_filter=partner_ids,
                exclude_reconcile=False)

        ledger_lines = self._compute_partner_ledger_lines(
            accounts, main_filter, target_move, start, stop,
            partner_filter=partner_ids,
            group_invoice_payments=group_invoice_payments)
        objects = self.pool.get('account.account').browse(self.cursor,
                                                          self.uid,
                                                          accounts)

        init_balance = {}
        ledger_lines_dict = {}
        partners_order = {}
        for account in objects:
            ledger_lines_dict[account.id] = ledger_lines.get(account.id, {})
            init_balance[account.id] = initial_balance_lines.get(account.id,
                                                                 {})
            # we have to compute partner order based on inital balance
            # and ledger line as we may have partner with init bal
            # that are not in ledger line and vice versa
            ledg_lines_pids = ledger_lines.get(account.id, {}).keys()
            if initial_balance_mode:
                non_null_init_balances = dict(
                    [(ib, amounts) for ib, amounts
                     in init_balance[account.id].iteritems()
                     if amounts['init_balance'] or
                     amounts['init_balance_currency']])
                init_bal_lines_pids = non_null_init_balances.keys()
            else:
                init_balance[account.id] = {}
                init_bal_lines_pids = []

            partners_order[account.id] = self._order_partners(
                ledg_lines_pids, init_bal_lines_pids)

        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'start_date': start_date,
            'stop_date': stop_date,
            'start_period': start_period,
            'stop_period': stop_period,
            'partner_ids': partner_ids,
            'chart_account': chart_account,
            'initial_balance_mode': initial_balance_mode,
            'init_balance': init_balance,
            'ledger_lines': ledger_lines_dict,
            'partners_order': partners_order,
        })

        return super(PartnersLedgerWebkit, self).set_context(
            objects, data, new_ids, report_type=report_type)

    def _compute_partner_ledger_lines(self, accounts_ids, main_filter,
                                      target_move, start, stop,
                                      partner_filter=False,
                                      group_invoice_payments=False):
        res = defaultdict(dict)

        for acc_id in accounts_ids:
            move_line_ids = self.get_partners_move_lines_ids(
                acc_id, main_filter, start, stop, target_move,
                exclude_reconcile=False, partner_filter=partner_filter)
            if not move_line_ids:
                continue
            for partner_id in move_line_ids:
                partner_line_ids = move_line_ids.get(partner_id, [])
                lines = self._get_move_line_datas(list(set(partner_line_ids)))
                if group_invoice_payments:
                    lines = self.group_lines(lines)
                res[acc_id][partner_id] = lines
        return res

    def group_lines(self, lines):
        grouped_lines = []
        for line in lines:
            for l in [x for x in lines if x['id'] != line['id']]:
                if l['lperiod_id'] == line['lperiod_id'] and \
                        l['jcode'] == line['jcode'] and \
                        l['ldate'] == line['ldate'] and \
                        l['rec_id'] == line['rec_id'] and \
                        l['currency_id'] == line['currency_id'] and \
                        l['partner_name'] == line['partner_name'] and \
                        l['lname'] == line['lname'] and \
                        l['peropen'] == line['peropen'] and \
                        l['account_id'] == line['account_id'] and \
                        l['invoice_type'] == line['invoice_type'] and \
                        l['move_name'] == line['move_name'] and \
                        l['invoice_number'] == line['invoice_number'] and \
                        l['move_id'] == line['move_id'] and \
                        l['rec_name'] == line['rec_name'] and \
                        l['lpartner_id'] == line['lpartner_id'] and \
                        l['invoice_id'] == line['invoice_id'] and \
                        l['jtype'] == line['jtype'] and \
                        l['period_code'] == line['period_code'] and \
                        l['lref'] == line['lref'] and \
                        l['currency_code'] == line['currency_code']:
                    line['debit'] += l['debit']
                    line['credit'] += l['credit']
                    line['amount_currency'] += l['amount_currency']
                    line['balance'] += l['balance']
                    line['date_maturity'] == ''
                    lines.remove(l)
            grouped_lines.append(line)
        return grouped_lines

HeaderFooterTextWebKitParser(
    'report.account.account_report_partners_ledger_webkit',
    'account.account',
    'addons/account_financial_report_webkit/report/templates/\
                                        account_report_partners_ledger.mako',
    parser=PartnersLedgerWebkit)
