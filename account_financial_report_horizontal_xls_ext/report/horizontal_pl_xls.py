# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
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

import xlwt
import time
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.addons.account_financial_report_horizontal_ext.report.account_profit_loss import report_pl_account_horizontal
from openerp.tools.translate import _


class my_report_pl_account_horizontal(report_pl_account_horizontal):

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a ledger_lines attribute on each browse record that will be used
        by mako template"""
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] \
                and data['form']['chart_account_id'] \
                and [data['form']['chart_account_id'][0]] or []
            result = self.get_data(data)
            objects = result.result_temp
            objects.append({'result': result.res_pl})
            lang_dict = self.pool.get('res.users').read(
                self.cr, self.uid, self.uid, ['context_lang'])
            data['lang'] = lang_dict.get('context_lang') or False

        self.localcontext.update({'objects': objects})

        return True


class trial_balance_xls(report_xls):
    column_sizes = [12, 30, 17, 17, 17, 17,
                    12, 30, 17, 17, 17, 17]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet('PL Report')  # _p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = ' - '.join(['PL Report'.upper(), _p.company.partner_id.name, _p.company.currency_id.name])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

        # write empty row to define column sizes
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None) for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)

        # Header Table
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])

        c_specs = [
            ('fy', 1, 0, 'text', _('Fiscal Year')),
            ('df', 2, 0, 'text', _('Filter')),
#                               data['form'].get('filter', False) == 'filter_date' and _('Dates Filter')
#                               or data['form'].get('filter', False) == 'filter_period' and _('Periods Filter')
#                               or u''),
#             ('ib', 1, 0, 'text', _('Initial Balance'), None, cell_style_center),
#             ('coa', 1, 0, 'text', _('Chart of Account'), None, cell_style_center),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

        cell_format = _xs['borders_all'] + _xs['wrap'] + _xs['top']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('fy', 1, 0, 'text', _p.get_fiscalyear(data) if _p.get_fiscalyear(data) else '-'),
#             ('af', 2, 0, 'text', _p.accounts(data) and ', '.join([account.code for account in _p.accounts(data)]) or _('All')),
        ]
        df = _('From') + ': '
        dt = _('To') + ': '
        if data['form'].get('filter', False) == 'filter_date':
            df += _p.get_start_date(data) if _p.get_start_date(data) else u''
            dt += _p.get_end_date(data) if _p.get_end_date(data) else u''
        elif data['form'].get('filter', False) == 'filter_period':
            df += _p.get_start_period(data) if _p.get_start_period(data) else u''
            dt += _p.get_end_period(data) if _p.get_end_period(data) else u''
        else:
            df += u''
            dt += u''

        c_specs += [
            ('df', 1, 0, 'text', df),
            ('dt', 1, 0, 'text', dt),
#             ('tm', 2, 0, 'text', _p.display_target_move(data), None, cell_style_center), _
#             ('ib', 1, 0, 'text', initial_balance_text[_p.initial_balance_mode], None, cell_style_center),
#             ('coa', 1, 0, 'text', p.get_chart_account(data), None, cell_style_center),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['wrap'] + _xs['top']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        account_span = 3
        c_specs = [
            ('c_code', 1, 0, 'text', _('Code')),
            ('c_account', account_span, 0, 'text', _('Account')),
            ('total_credit', 1, 0, 'text', _('Total Expense'), None, cell_style_right),
            ('credit', 1, 0, 'text', _('Expense'), None, cell_style_right),
            ('d_code', 1, 0, 'text', _('Code')),
            ('d_account', account_span, 0, 'text', _('Account')),
            ('total_debit', 1, 0, 'text', _('Total Revenue'), None, cell_style_right),
            ('debit', 1, 0, 'text', _('Revenue'), None, cell_style_right)]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        ws.set_horz_split_pos(row_pos)

        # cell styles for account data
        view_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        view_cell_style = xlwt.easyxf(view_cell_format)
        view_cell_style_center = xlwt.easyxf(view_cell_format + _xs['center'])
        view_cell_style_decimal = xlwt.easyxf(view_cell_format + _xs['right'], num_format_str = report_xls.decimal_format)
        view_cell_style_pct = xlwt.easyxf(view_cell_format + _xs['center'], num_format_str = '0')
        regular_cell_format = _xs['borders_all']
        regular_cell_style = xlwt.easyxf(regular_cell_format)
        regular_cell_style_center = xlwt.easyxf(regular_cell_format + _xs['center'])
        regular_cell_style_decimal = xlwt.easyxf(regular_cell_format + _xs['right'], num_format_str = report_xls.decimal_format)
        regular_cell_style_pct = xlwt.easyxf(regular_cell_format + _xs['center'], num_format_str = '0')
        account_id = data['form'].get('chart_account_id', False)
        if account_id:
            account_id = account_id[0]
        chart = self.pool['account.chart.template'].browse(self.cr, 1, account_id)
        partners = [
            chart.property_account_payable.code,
            chart.property_account_receivable.code,
        ]
        result = objects.pop()
        for row in objects:
            if row:
                # expense
                if row['type'] == 'view' and not row['code'] in partners:
                    c_specs = [
                        ('c_code', 1, 0, 'text', row['code'], None, view_cell_style),
                        ('c_account', account_span, 0, 'text', row['name'], None, view_cell_style),
                        ('total_credit', 1, 0, 'number', row['balance'], None, view_cell_style_decimal),
                        ('credit', 1, 0, 'text', None, None, view_cell_style),
                    ]
                else:
                    c_specs = [
                        ('c_code', 1, 0, 'text', row['code'], None, regular_cell_style),
                        ('c_account', account_span, 0, 'text', row['name'], None, regular_cell_style),
                        ('total_credit', 1, 0, 'text', None, None, regular_cell_style),
                        ('credit', 1, 0, 'number', row['balance'], None, regular_cell_style_decimal),
                    ]
                # revenue
                if row['type1'] == 'view' and not row['code1'] in partners:
                    c_specs += [
                        ('d_code', 1, 0, 'text', row['code1'], None, view_cell_style),
                        ('d_account', account_span, 0, 'text', row['name1'], None, view_cell_style),
                        ('total_debit', 1, 0, 'number', row['balance1'], None, view_cell_style_decimal),
                        ('debit', 1, 0, 'text', None, None, view_cell_style),
                    ]
                else:
                    c_specs += [
                        ('d_code', 1, 0, 'text', row['code1'], None, regular_cell_style),
                        ('d_account', account_span, 0, 'text', row['name1'], None, regular_cell_style),
                        ('total_debit', 1, 0, 'text', None, None, regular_cell_style),
                        ('debit', 1, 0, 'number', row['balance1'], None, regular_cell_style_decimal),
                    ]

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

        # print totals and result
        d_tot_formula = 'sum(' + rowcol_to_cell(5, 5) + ':' + rowcol_to_cell(row_pos - 1, 5) + ')'
        c_tot_formula = 'sum(' + rowcol_to_cell(5, 11) + ':' + rowcol_to_cell(row_pos - 1, 11) + ')'
        c_specs = [
            ('c_code', 1, 0, 'text', None, None, view_cell_style),
            ('c_account', account_span, 0, 'text', _('Expense Totals'), None, view_cell_style),
            ('total_credit', 1, 0, 'text', None, None, view_cell_style),
            ('credit', 1, 0, 'number', None, d_tot_formula, view_cell_style_decimal),
            ('d_code', 1, 0, 'text', None, None, view_cell_style),
            ('d_account', account_span, 0, 'text', _('Revenue Totals'), None, view_cell_style),
            ('total_debit', 1, 0, 'text', None, None, view_cell_style),
            ('debit', 1, 0, 'number', None, c_tot_formula, view_cell_style_decimal)]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        res = result['result']
        profit = False
        if res.get('type', False) == 'Utile':
            profit = True
        c_specs = [
            ('c_code', 1, 0, 'text', None, None, view_cell_style),
            ('c_account', account_span, 0, 'text', profit and res.get('type', False) or None, None, view_cell_style),
            ('total_credit', 1, 0, 'text', None, None, view_cell_style),
            ('credit', 1, 0, 'number', profit and res.get('balance', False) or None, None, view_cell_style_decimal),
            ('d_code', 1, 0, 'text', None, None, view_cell_style),
            ('d_account', account_span, 0, 'text', not profit and res.get('type', False) or None, None, view_cell_style),
            ('total_debit', 1, 0, 'text', None, None, view_cell_style),
            ('debit', 1, 0, 'number', not profit and res.get('balance', False) or None, None, view_cell_style_decimal),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

        d_tot_formula = 'sum(' + rowcol_to_cell(row_pos - 2, 5) + ':' + rowcol_to_cell(row_pos - 1, 5) + ')'
        c_tot_formula = 'sum(' + rowcol_to_cell(row_pos - 2, 5) + ':' + rowcol_to_cell(row_pos - 1, 5) + ')'
        c_specs = [
            ('c_code', 1, 0, 'text', None, None, view_cell_style),
            ('c_account', account_span, 0, 'text', _('Totals'), None, view_cell_style),
            ('total_credit', 1, 0, 'text', None, None, view_cell_style),
            ('credit', 1, 0, 'number', None, d_tot_formula, view_cell_style_decimal),
            ('d_code', 1, 0, 'text', None, None, view_cell_style),
            ('d_account', account_span, 0, 'text', _('Totals'), None, view_cell_style),
            ('total_debit', 1, 0, 'text', None, None, view_cell_style),
            ('debit', 1, 0, 'number', None, c_tot_formula, view_cell_style_decimal)]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)

trial_balance_xls('report.account.account_report_horizontal_pl_xls', 'account.account',
    parser=my_report_pl_account_horizontal)
