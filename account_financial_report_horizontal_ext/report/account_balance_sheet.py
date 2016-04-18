# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>),
#    Copyright (C) 2012 Therp BV (<http://therp.nl>),
#    Copyright (C) 2013 Agile Business Group sagl
#    (<http://www.agilebg.com>) (<lorenzo.battistini@agilebg.com>)
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

import time

from openerp.report import report_sxw
from openerp.addons.account_financial_report_horizontal_ext.report import (
    account_profit_loss
)
from common_report_header import common_report_header
from openerp.tools.translate import _


class report_balancesheet_horizontal(
    report_sxw.rml_parse, common_report_header
):

    def __init__(self, cr, uid, name, context=None):
        super(report_balancesheet_horizontal, self).__init__(
            cr, uid, name, context=context)
        self.obj_pl = account_profit_loss.report_pl_account_horizontal(
            cr, uid, name, context=context)
        self.result_sum_dr = 0.0
        self.result_sum_cr = 0.0
        self.result = {}
        self.res_bl = {}
        self.result_temp = []
        self.result_loss = []
        self.result_profit = []
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'get_lines_another': self.get_lines_another,
            'get_profit': self.get_profit,
            'get_loss': self.get_loss,
            'sum_dr': self.sum_dr,
            'sum_cr': self.sum_cr,
            'sum_partial_dr': self.sum_partial_dr,
            'sum_partial_cr': self.sum_partial_cr,
            'get_data': self.get_data,
            'get_pl_balance': self.get_pl_balance,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_sortby': self._get_sortby,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if data['model'] == 'ir.ui.menu':
            new_ids = 'chart_account_id' in data['form'] \
                and data['form']['chart_account_id'] \
                and [data['form']['chart_account_id'][0]] or []
            objects = self.pool.get('account.account').browse(
                self.cr, self.uid, new_ids)
            lang_dict = self.pool.get('res.users').read(
                self.cr, self.uid, self.uid, ['lang'])
            data['lang'] = lang_dict.get('lang') or False
            chart_id = 'chart_template_id' in data['form'] \
                  and data['form']['chart_template_id'] \
                  and [data['form']['chart_template_id'][0]] or []
            data['chart'] = self.pool['account.chart.template'].browse(self.cr, self.uid, chart_id)
        return super(
            report_balancesheet_horizontal, self
        ).set_context(objects, data, new_ids, report_type=report_type)

    def sum_partial_dr(self):
        return self.result_sum_dr

    def sum_partial_cr(self):
        return self.result_sum_cr

    def sum_dr(self):
        if self.res_bl['type'] == _('Net Profit'):
            self.result_sum_dr += self.res_bl['balance']
        return self.result_sum_dr

    def sum_cr(self):
        if self.res_bl['type'] == _('Net Loss'):
            self.result_sum_cr += self.res_bl['balance']
        return self.result_sum_cr

    def get_pl_balance(self):
        return self.res_bl

    def get_data(self, data):
        cr, uid = self.cr, self.uid

        # Getting Profit or Loss Balance from profit and Loss report
        self.obj_pl.get_data(data)
        self.res_bl = self.obj_pl.final_result()

        account_pool = self.pool['account.account']
        currency_pool = self.pool['res.currency']

        types = [
            'liability',
            'asset'
        ]

        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form'].get('fiscalyear_id', False)
        if ctx['fiscalyear']:
            ctx['fiscalyear'] = ctx['fiscalyear'][0]

        if data['form']['filter'] == 'filter_period':
            ctx['periods'] = data['form'].get('periods', False)
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form'].get('date_from', False)
            ctx['date_to'] = data['form'].get('date_to', False)
        ctx['state'] = data['form'].get('target_move', 'all')
        cal_list = {}
        account_dict = {}
        chart = data['chart']
        rec_account = chart.property_account_receivable
        pay_account = chart.property_account_payable

        account_ids = account_pool.search(cr, uid, [('parent_id', '=', False)])
        if account_ids:
            account_id = account_ids[0]

        account_ids = account_pool._get_children_and_consol(
            cr, uid, account_id, context=ctx)
        accounts = account_pool.browse(cr, uid, account_ids, context=ctx)

        if not self.res_bl:
            self.res_bl['type'] = _('Net Profit')
            self.res_bl['balance'] = 0.0

        if self.res_bl['type'] == _('Net Profit'):
            self.res_bl['type'] = _('Net Profit')
        else:
            self.res_bl['type'] = _('Net Loss')
        pl_dict = {
            'code': self.res_bl['type'],
            'name': self.res_bl['type'],
            'level': False,
            'balance': self.res_bl['balance'],
            'type': self.res_bl['type'],
        }

        accounts_l_temp = {}
        accounts_a_temp = {}
        for typ in types:
            for account in accounts:
                # Show normal accounts
                if account.user_type.report_type and account.user_type.report_type == typ and (
                    account.parent_id.code != rec_account.code) and (
                    account.parent_id.code != pay_account.code) and (
                    account.code != rec_account.code) and (
                    account.code != pay_account.code
                ):
                    account_dict = {
                        'id': account.id,
                        'code': account.code,
                        'name': account.name,
                        'level': account.level,
                        'balance': (
                            account.balance and typ == 'liability' and -1 or 1
                        ) * account.balance,
                        'type': account.type,
                        'parent_id': account.parent_id.id,
                        'parent_code': account.parent_id.code,
                    }
                    account_parent_dict = {
                        'id': account_dict['parent_id'],
                        'balance': account_dict['balance'],
                        'code': account.parent_id.code,
                        'name': account.parent_id.name,
                        'level': account.parent_id.level,
                        'type': account.parent_id.type,
                        'parent_id': account.parent_id.parent_id.id,
                        'parent_code': account.parent_id.code,
                    }
                    currency = (account.currency_id and account.currency_id or account.company_id.currency_id)

                    #sum negative asset as positive in liability and viceversa
                    if (typ == 'liability' and account_dict['balance'] >= 0.0 or
                        typ == 'asset' and account_dict['balance'] < 0.0
                        ) and account.type != 'view' and (account.debit != account.credit):
                            self.result_sum_dr += (typ == 'liability' and 1 or -1) * account_dict['balance']
                    if (typ == 'asset' and account_dict['balance'] >= 0.0 or
                        typ == 'liability' and account_dict['balance'] < 0.0
                        ) and account.type != 'view' and (account.debit != account.credit):
                        self.result_sum_cr += (typ == 'asset' and 1 or -1) * account_dict['balance']

                    if data['form']['display_account'] == 'bal_movement':
                        if (not currency_pool.is_zero(
                                self.cr, self.uid, currency, account.credit
                            )) or (not currency_pool.is_zero(
                                    self.cr, self.uid, currency, account.debit
                            )) or (not currency_pool.is_zero(
                                    self.cr, self.uid, currency,
                                    account.balance)):
                            previous_balance = 0.0
                            if (typ == 'liability' and account_dict['balance'] > 0.0) or (typ == 'asset' and account_dict['balance'] < 0.0):
                                if  account_dict['balance'] < 0.0:
                                    account_dict.update({'balance': account_dict['balance'] * -1})
                                    account_parent_dict.update({'balance': account_parent_dict['balance'] * -1})
                                if accounts_l_temp:
                                    if account_dict['parent_id'] in accounts_l_temp:
                                        previous_balance = accounts_l_temp[account_dict['parent_id']]['balance']
                                        account_parent_dict.update({'balance': previous_balance + account_dict['balance']})
                                accounts_l_temp.update({account_dict['parent_id']: account_parent_dict})
                                accounts_l_temp.update({account_dict['id']: account_dict})
                            elif (typ == 'asset' and account_dict['balance'] > 0.0) or (typ == 'liability' and account_dict['balance'] < 0.0):
                                if  account_dict['balance'] < 0.0:
                                    account_dict.update({'balance': account_dict['balance'] * -1})
                                    account_parent_dict.update({'balance': account_parent_dict['balance'] * -1})
                                if accounts_a_temp:
                                    if account_dict['parent_id'] in accounts_a_temp:
                                        previous_balance = accounts_a_temp[account_dict['parent_id']]['balance']
                                        account_parent_dict.update({'balance': previous_balance + account_dict['balance']})
                                accounts_a_temp.update({account_dict['parent_id']: account_parent_dict})
                                accounts_a_temp.update({account_dict['id']: account_dict})    
                                
                    elif data['form']['display_account'] == 'bal_solde':
                        if not currency_pool.is_zero(
                            self.cr, self.uid, currency, account.balance):
                            #update positive liability or negative asset in liability column
                            previous_balance = 0.0
                            if (typ == 'liability' and account_dict['balance'] > 0.0) or (typ == 'asset' and account_dict['balance'] < 0.0):
                                if  account_dict['balance'] < 0.0:
                                    account_dict.update({'balance': account_dict['balance'] * -1})
                                    account_parent_dict.update({'balance': account_parent_dict['balance'] * -1})
                                if accounts_l_temp:
                                    if account_dict['parent_id'] in accounts_l_temp:
                                        previous_balance = accounts_l_temp[account_dict['parent_id']]['balance']
                                        account_parent_dict.update({'balance': previous_balance + account_dict['balance']})
                                accounts_l_temp.update({account_dict['parent_id']: account_parent_dict})
                                accounts_l_temp.update({account_dict['id']: account_dict})
                            elif (typ == 'asset' and account_dict['balance'] > 0.0) or (typ == 'liability' and account_dict['balance'] < 0.0):
                                if  account_dict['balance'] < 0.0:
                                    account_dict.update({'balance': account_dict['balance'] * -1})
                                    account_parent_dict.update({'balance': account_parent_dict['balance'] * -1})
                                if accounts_a_temp:
                                    if account_dict['parent_id'] in accounts_a_temp:
                                        previous_balance = accounts_a_temp[account_dict['parent_id']]['balance']
                                        account_parent_dict.update({'balance': previous_balance + account_dict['balance']})
                                accounts_a_temp.update({account_dict['parent_id']: account_parent_dict})
                                accounts_a_temp.update({account_dict['id']: account_dict})    

                    else:
                            previous_balance = 0.0
                            if (typ == 'liability' and account_dict['balance'] > 0.0) or (typ == 'asset' and account_dict['balance'] < 0.0):
                                if  account_dict['balance'] < 0.0:
                                    account_dict.update({'balance': account_dict['balance'] * -1})
                                    account_parent_dict.update({'balance': account_parent_dict['balance'] * -1})
                                if accounts_l_temp:
                                    if account_dict['parent_id'] in accounts_l_temp:
                                        previous_balance = accounts_l_temp[account_dict['parent_id']]['balance']
                                        account_parent_dict.update({'balance': previous_balance + account_dict['balance']})
                                accounts_l_temp.update({account_dict['parent_id']: account_parent_dict})
                                accounts_l_temp.update({account_dict['id']: account_dict})
                            elif (typ == 'asset' and account_dict['balance'] > 0.0) or (typ == 'liability' and account_dict['balance'] < 0.0):
                                if  account_dict['balance'] < 0.0:
                                    account_dict.update({'balance': account_dict['balance'] * -1})
                                    account_parent_dict.update({'balance': account_parent_dict['balance'] * -1})
                                if accounts_a_temp:
                                    if account_dict['parent_id'] in accounts_a_temp:
                                        previous_balance = accounts_a_temp[account_dict['parent_id']]['balance']
                                        account_parent_dict.update({'balance': previous_balance + account_dict['balance']})
                                accounts_a_temp.update({account_dict['parent_id']: account_parent_dict})
                                accounts_a_temp.update({account_dict['id']: account_dict})    

            
            #add supplier and customer total
            if typ == 'liability':
                account_view_id = account_pool.search(cr, uid, [('code', '=', pay_account.code)])
            if typ == 'asset':
                account_view_id = account_pool.search(cr, uid, [('code', '=', rec_account.code)])
            account_view = account_pool.browse(cr, uid, account_view_id[0], context=ctx)
            account_dict = {
                    'id': account_view.id,
                    'code': account_view.code,
                    'name': account_view.name,
                    'level': account_view.level,
                    'balance': (
                        account_view.balance and typ == 'liability' and -1 or 1
                    ) * account_view.balance,
                    'type': account_view.type,
                    'parent_id': account_view.parent_id.id,
                    'parent_code': account_view.code,
                }
            if typ == 'liability':
                self.result_sum_dr += account_dict['balance']
                accounts_l_temp.update({account_dict['id']: account_dict})
            if typ == 'asset':
                self.result_sum_cr += account_dict['balance']
                accounts_a_temp.update({account_dict['id']: account_dict})
        
        account_l_temp = accounts_l_temp.values()
        account_a_temp = accounts_a_temp.values()
        cal_list['asset'] = self.result['asset'] = sorted(account_a_temp, key = lambda k: [k['parent_code'], k['level'], k['code']])
        cal_list['liability'] = self.result['liability'] = sorted(account_l_temp, key = lambda k: [k['parent_code'], k['level'], k['code']])

        if pl_dict['code'] == _('Net Loss'):
            self.result_loss.append(pl_dict)
        else:
            self.result_profit.append(pl_dict)

        if cal_list:
            temp = {}
            for i in range(
                0, max(len(cal_list['liability']), len(cal_list['asset']))
            ):
                if i < len(cal_list['liability']) and i < len(
                    cal_list['asset']
                ):
                    temp = {
                        'code': cal_list['liability'][i]['code'],
                        'name': cal_list['liability'][i]['name'],
                        'level': cal_list['liability'][i]['level'],
                        'balance': cal_list['liability'][i]['balance'],
                        'type': cal_list['liability'][i]['type'],
                        'code1': cal_list['asset'][i]['code'],
                        'name1': cal_list['asset'][i]['name'],
                        'level1': cal_list['asset'][i]['level'],
                        'balance1': cal_list['asset'][i]['balance'],
                        'type1': cal_list['asset'][i]['type'],
                    }
                    self.result_temp.append(temp)
                else:
                    if i < len(cal_list['asset']):
                        temp = {
                            'code': '',
                            'name': '',
                            'level': False,
                            'balance': False,
                            'type': False,
                            'code1': cal_list['asset'][i]['code'],
                            'name1': cal_list['asset'][i]['name'],
                            'level1': cal_list['asset'][i]['level'],
                            'balance1': cal_list['asset'][i]['balance'],
                            'type1': cal_list['asset'][i]['type'],
                        }
                        self.result_temp.append(temp)
                    if i < len(cal_list['liability']):
                        temp = {
                            'code': cal_list['liability'][i]['code'],
                            'name': cal_list['liability'][i]['name'],
                            'level': cal_list['liability'][i]['level'],
                            'balance': cal_list['liability'][i]['balance'],
                            'type': cal_list['liability'][i]['type'],
                            'code1': '',
                            'name1': '',
                            'level1': False,
                            'balance1': False,
                            'type1': False,
                        }
                        self.result_temp.append(temp)

        if self.context.get('xls_export', False):
            return self
        else:
            return None

    def get_lines(self):
        return self.result_temp

    def get_lines_another(self, group):
        return self.result.get(group, [])

    def get_profit(self):
        return self.result_profit

    def get_loss(self):
        return self.result_loss

report_sxw.report_sxw(
    'report.account.balancesheet.horizontal', 'account.account',
    'addons/account_financial_report_horizontal_ext/report/'
    'account_balance_sheet_horizontal.rml',
    parser=report_balancesheet_horizontal,
    header='internal landscape')

report_sxw.report_sxw(
    'report.account.balancesheet', 'account.account',
    'addons/account_financial_report_horizontal_ext/report/'
    'account_balance_sheet.rml',
    parser=report_balancesheet_horizontal,
    header='internal')