# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp.osv import orm, fields
from openerp.tools.float_utils import float_round, float_compare
from openerp.tools.translate import _
from decimal import Decimal, ROUND_UP
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time

import openerp.addons.decimal_precision as dp


class dummy_fy(object):
    def __init__(self, *args, **argv):
        for key, arg in argv.items():
            setattr(self, key, arg)


class account_asset_category(orm.Model):
    _inherit = 'account.asset.category'

    def _get_method_time(self, cr, uid, context=None):
        return [
            ('year', _('Number of Years')),
            ('percent', _('Percent'))
        ]

    _columns = {
        'method_number': fields.integer(
            'Number of Depreciations/Years',
            help="The number of depreciations/years needed to depreciate your asset"),
        'method_number_percent': fields.float(
            ' Percentage Depreciation - method Percent.',
            help="Percentage depreciation in method Percent."),
        'method_time': fields.selection(_get_method_time, 'Time Method', required=True,
            help="Choose the method to use to compute the dates and number of depreciation lines.\n"
                 "  * Number of Years: Specify the number of years for the depreciation.\n"
                 "  * Percent: Percentage depreciation per period (e.g. 25 = 25%)."
                 "\nThe 'Number of Years' method is for Financial Assets whereas "
                 " you should use the 'Number of Depreciations' and 'Ending Date' " 
                 "for Deferred Expenses or Deferred Income purposes."),
        'first_year_half_rata': fields.boolean(
            'First Year Half Rata',
            help='Indicates that the first depreciation entry for this asset has to be done half value.'),
    }

    _defaults = {
        'method_number_percent': 20,
        'method_time': 'percent',
    }

    def onchange_method_time(self, cr, uid, ids,
                             method_time='number', context=None):
        res = {'value': {}}
#         if method_time != 'year':
#             res['value'] = {'prorata': True}
        return res

    def create(self, cr, uid, vals, context=None):
        if 'method_time' in vals:
            if vals.get('method_time') == 'percent' and not vals.get('prorata'):
                vals['prorata'] = False
        return super(account_asset_category, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if 'method_time' in vals:
            if vals.get('method_time') == 'percent' and not vals.get('prorata'):
                vals['prorata'] = False
        return super(account_asset_category, self).write(cr, uid, ids, vals, context)


class account_asset_asset(orm.Model):
    _inherit = 'account.asset.asset'

    def _get_depreciation_stop_date(self, cr, uid, asset,
                                    depreciation_start_date,
                                    context=None):
        depreciation_stop_date = super(account_asset_asset, self)._get_depreciation_stop_date(cr, uid, asset,
                                    depreciation_start_date=depreciation_start_date, context=context)
        if 'lost_year' in context:
            lost_year = context['lost_year']
        if asset.method_time == 'percent':
            if asset.method_period == 'month':
                depreciation_stop_date = depreciation_start_date + relativedelta(
                    months=int(Decimal(str(100 / asset.method_number_percent)).quantize(Decimal('1'), rounding=ROUND_UP)), days=-1)
            elif asset.method_period == 'quarter':
                depreciation_stop_date = depreciation_start_date + relativedelta(
                    months=int(Decimal(str(100 / asset.method_number_percent * 3)).quantize(Decimal('1'), rounding=ROUND_UP)), days=-1)
            elif asset.method_period == 'year':
                depreciation_stop_date = depreciation_start_date + relativedelta(
                    years=int(Decimal(str(100 / asset.method_number_percent)).quantize(Decimal('1'), rounding=ROUND_UP)) + lost_year, days=-1)
        return depreciation_stop_date

    def _compute_year_amount(self, cr, uid, asset, amount_to_depr,
                             residual_amount, context=None):
        super(account_asset_asset, self)._compute_year_amount(
            cr, uid, asset, amount_to_depr,
            residual_amount, context=context)
        if asset.method_time == 'year':
            divisor = asset.method_number
        elif asset.method_time == 'number':
            if asset.method_period == 'month':
                divisor = asset.method_number / 12.0
            elif asset.method_period == 'quarter':
                divisor = asset.method_number * 3 / 12.0
            elif asset.method_period == 'year':
                divisor = asset.method_number
        elif asset.method_time == 'end':
            duration = \
                (datetime.strptime(asset.method_end, '%Y-%m-%d') -
                 datetime.strptime(asset.date_start, '%Y-%m-%d')).days + 1
            divisor = duration / 365.0
        #new
        elif asset.method_time == 'percent':
            divisor = False
            if asset.method_period == 'month':
                percent = asset.method_number_percent * 12.0 / 100.0
            elif asset.method_period == 'quarter':
                percent = asset.method_number_percent / 3 * 12 / 100.0
            elif asset.method_period == 'year':
                percent = asset.method_number_percent / 100.0
        if divisor:
            year_amount_linear = amount_to_depr / divisor
        else:
            year_amount_linear = amount_to_depr * percent
        #endnew
        if asset.method == 'linear':
            return year_amount_linear
        year_amount_degressive = residual_amount * \
            asset.method_progress_factor
        if asset.method == 'degressive':
            return year_amount_degressive
        if asset.method == 'degr-linear':
            if year_amount_linear > year_amount_degressive:
                return year_amount_linear
            else:
                return year_amount_degressive
        else:
            raise orm.except_orm(
                _('Programming Error!'),
                _("Illegal value %s in asset.method.") % asset.method)

    def _compute_depreciation_table(self, cr, uid, asset, context=None):
        if not context:
            context = {}

        table = []
        if not asset.method_number:
            return table

        context['company_id'] = asset.company_id.id
        fy_obj = self.pool.get('account.fiscalyear')
        init_flag = False
        try:
            fy_id = fy_obj.find(cr, uid, asset.date_start, context=context)
            fy = fy_obj.browse(cr, uid, fy_id)
            if fy.state == 'done':
                init_flag = True
            fy_date_start = datetime.strptime(fy.date_start, '%Y-%m-%d')
            fy_date_stop = datetime.strptime(fy.date_stop, '%Y-%m-%d')
        except:
            # The following logic is used when no fiscalyear
            # is defined for the asset start date:
            # - We lookup the first fiscal year defined in the system
            # - The 'undefined' fiscal years are assumed to be years
            # with a duration equals to calendar year
            cr.execute(
                "SELECT id, date_start, date_stop "
                "FROM account_fiscalyear ORDER BY date_stop ASC LIMIT 1")
            first_fy = cr.dictfetchone()
            first_fy_date_start = datetime.strptime(
                first_fy['date_start'], '%Y-%m-%d')
            asset_date_start = datetime.strptime(asset.date_start, '%Y-%m-%d')
            fy_date_start = first_fy_date_start
            if asset_date_start > fy_date_start:
                asset_ref = asset.code and '%s (ref: %s)' \
                    % (asset.name, asset.code) or asset.name
                raise orm.except_orm(
                    _('Error!'),
                    _("You cannot compute a depreciation table for an asset "
                      "starting in an undefined future fiscal year."
                      "\nPlease correct the start date for asset '%s'.")
                    % asset_ref)
            while asset_date_start < fy_date_start:
                fy_date_start = fy_date_start - relativedelta(years=1)
            fy_date_stop = fy_date_start + relativedelta(years=1, days=-1)
            fy_id = False
            fy = dummy_fy(
                date_start=fy_date_start.strftime('%Y-%m-%d'),
                date_stop=fy_date_stop.strftime('%Y-%m-%d'),
                id=False,
                state='done',
                dummy=True)
            init_flag = True
        #new
        lost_year = 0
        fy_half_rata = asset.first_year_half_rata
        if context.get('lost_year', False):
            lost_year = int(context.get('lost_year'))
        elif fy_half_rata:
            lost_year += 1
        context.update({'lost_year': lost_year})
        #endnew
        depreciation_start_date = self._get_depreciation_start_date(
            cr, uid, asset, fy, context=context)
        depreciation_stop_date = self._get_depreciation_stop_date(
            cr, uid, asset, depreciation_start_date, context=context)

        while fy_date_start <= depreciation_stop_date:
            table.append({
                'fy_id': fy_id,
                'date_start': fy_date_start,
                'date_stop': fy_date_stop,
                'init': init_flag})
            fy_date_start = fy_date_stop + relativedelta(days=1)
            try:
                fy_id = fy_obj.find(cr, uid, fy_date_start, context=context)
                init_flag = False
            except:
                fy_id = False
            if fy_id:
                fy = fy_obj.browse(cr, uid, fy_id)
                if fy.state == 'done':
                    init_flag = True
                fy_date_stop = datetime.strptime(fy.date_stop, '%Y-%m-%d')
            else:
                fy_date_stop = fy_date_stop + relativedelta(years=1)

        digits = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
        amount_to_depr = residual_amount = asset.asset_value

        # step 1: calculate depreciation amount per fiscal year
        fy_residual_amount = residual_amount
        i_max = len(table) - 1
        asset_sign = asset.asset_value >= 0 and 1 or -1
        for i, entry in enumerate(table):
            year_amount = self._compute_year_amount(
                cr, uid, asset, amount_to_depr,
                fy_residual_amount, context=context)
            if asset.method_period == 'year':
                period_amount = year_amount
            elif asset.method_period == 'quarter':
                period_amount = year_amount/4
            elif asset.method_period == 'month':
                period_amount = year_amount/12
            if i == i_max:
                fy_amount = fy_residual_amount
            else:
                firstyear = i == 0 and True or False
                fy_factor = self._get_fy_duration_factor(
                    cr, uid, entry, asset, firstyear, context=context)
                fy_amount = year_amount * fy_factor
                #new
                if fy_half_rata and i == 0:
                    fy_amount = fy_amount * 0.5 
                #endnew
            if asset_sign * (fy_amount - fy_residual_amount) > 0:
                fy_amount = fy_residual_amount
            period_amount = round(period_amount, digits)
            fy_amount = round(fy_amount, digits)
            #new
            if lost_year > 0 and not (fy_half_rata and lost_year == 1):
                period_amount = 0.0
                fy_amount = 0.0
                lost_year -= 1
            #endnew
            entry.update({
                'period_amount': period_amount,
                'fy_amount': fy_amount,
            })
            fy_residual_amount -= fy_amount
            if round(fy_residual_amount, digits) == 0:
                break
        i_max = i
        table = table[:i_max + 1]

        # step 2: spread depreciation amount per fiscal year
        # over the depreciation periods
        fy_residual_amount = residual_amount
        line_date = False
        for i, entry in enumerate(table):
            period_amount = entry['period_amount']
            fy_amount = entry['fy_amount']
            period_duration = (asset.method_period == 'year' and 12) \
                or (asset.method_period == 'quarter' and 3) or 1
            if period_duration == 12:
                if asset_sign * (fy_amount - fy_residual_amount) > 0:
                    fy_amount = fy_residual_amount
                lines = [{'date': entry['date_stop'], 'amount': fy_amount}]
                fy_residual_amount -= fy_amount
            elif period_duration in [1, 3]:
                lines = []
                fy_amount_check = 0.0
                if not line_date:
                    if period_duration == 3:
                        m = [x for x in [3, 6, 9, 12]
                             if x >= depreciation_start_date.month][0]
                        line_date = depreciation_start_date + \
                            relativedelta(month=m, day=31)
                    else:
                        line_date = depreciation_start_date + \
                            relativedelta(months=0, day=31)
                while line_date <= \
                        min(entry['date_stop'], depreciation_stop_date) and \
                        asset_sign * (fy_residual_amount - period_amount) > 0:
                    lines.append({'date': line_date, 'amount': period_amount})
                    fy_residual_amount -= period_amount
                    fy_amount_check += period_amount
                    line_date = line_date + \
                        relativedelta(months=period_duration, day=31)
                if i == i_max and \
                        (not lines or
                         depreciation_stop_date > lines[-1]['date']):
                    # last year, last entry
                    period_amount = fy_residual_amount
                    lines.append({'date': line_date, 'amount': period_amount})
                    fy_amount_check += period_amount
                if round(fy_amount_check - fy_amount, digits) != 0:
                    # handle rounding and extended/shortened
                    # fiscal year deviations
                    diff = fy_amount_check - fy_amount
                    fy_residual_amount += diff
                    if i == 0:  # first year: deviation in first period
                        lines[0]['amount'] = period_amount - diff
                    else:       # other years: deviation in last period
                        lines[-1]['amount'] = period_amount - diff
            else:
                raise orm.except_orm(
                    _('Programming Error!'),
                    _("Illegal value %s in asset.method_period.")
                    % asset.method_period)
            for line in lines:
                line['depreciated_value'] = amount_to_depr - residual_amount
                residual_amount -= line['amount']
                line['remaining_value'] = residual_amount
            entry['lines'] = lines

        return table

    def _asset_value_compute(self, cr, uid, asset, context=None):
        asset_value = super(account_asset_asset, self)._asset_value_compute(cr, uid, asset, context=context)
        if asset.type != 'view':
            asset_value = asset.purchase_value + asset.increase_value \
                - asset.salvage_value + asset.decrease_value \
                + asset.remove_value
        return asset_value

    def onchange_purchase_salvage_value(
            self, cr, uid, ids, purchase_value,
            salvage_value, increase_value, decrease_value, remove_value,
            date_start, context=None):
        if not context:
            context = {}
        val = {}
        purchase_value = purchase_value or 0.0
        salvage_value = salvage_value or 0.0
        increase_value = increase_value or 0.0
        decrease_value = decrease_value or 0.0
        remove_value = remove_value or 0.0
        if purchase_value or salvage_value or increase_value or decrease_value or remove_value:
            val['asset_value'] = purchase_value - salvage_value + increase_value + decrease_value + remove_value

        if ids:
            aadl_obj = self.pool.get('account.asset.depreciation.line')
            dl_create_ids = aadl_obj.search(
                cr, uid, [('type', '=', 'create'), ('asset_id', 'in', ids)])
            aadl_obj.write(
                cr, uid, dl_create_ids,
                {'amount': val['asset_value'], 'line_date': date_start})
        return {'value': val}

    def _asset_value(self, cr, uid, ids, name, args, context=None):
        return self._asset_value(cr, uid, ids, name, args, context=context)

    def _get_assets(self, cr, uid, ids, context=None):
        return self._get_assets(cr, uid, ids, context=context)

    def _get_method_time(self, cr, uid, context=None):
        return self.pool['account.asset.category']._get_method_time(
            cr, uid, context)

    _columns = {
        'purchase_value': fields.float(
            'Purchase Value', digits_compute=dp.get_precision('Account'),
            required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            help="\nThe Asset Value is calculated as follows:"
                 "\nPurchase Value - Salvage Value."),
        'increase_value': fields.float('Increase Value', digits_compute=dp.get_precision('Account'),
            required=False, readonly=True, states={'draft': [('readonly', False)]},),
        'decrease_value': fields.float('Decrease Value', digits_compute=dp.get_precision('Account'),
            required=False, readonly=True, states={'draft': [('readonly', False)]},),
        'remove_value': fields.float('Remove Value', digits_compute=dp.get_precision('Account'),
            required=False, readonly=True, states={'draft': [('readonly', False)]},),
        'asset_value': fields.function(
            _asset_value, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Asset Value',
            store={
                'account.asset.asset': (
                _get_assets,
                ['purchase_value', 'salvage_value', 'increase_value',
                'decrease_value', 'remove_value', 'parent_id'], 10),
            },
            help="The Asset Value is calculated as follows:\nPurchase Value - Salvage Value."),
        'method_number_percent': fields.float(
            'Percentage Depreciation',
            readonly=True, states={'draft': [('readonly', False)]},
            help="Percentage depreciation in method Percent."),
        'method_time': fields.selection(
            _get_method_time, 'Time Method',
            required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            help="Choose the method to use to compute the dates and "
                 "number of depreciation lines.\n"
                 "  * Number of Years: Specify the number of years "
                 "for the depreciation.\n"
                 "  * Percent: Percentage depreciation per period (25 = 25%)."
                 "\nThe 'Number of Years' method is for Financial Assets whereas"
                 " you should use the 'Number of Depreciations' and 'Ending "
                 "Date' for Deferred Expenses or Deferred Income purposes."),
        'first_year_half_rata': fields.boolean(
            'First Year Half Rata', readonly=True, states={'draft': [('readonly', False)]},
            help='Indicates that the first depreciation entry for this asset has to be done half value.'),
    }
    _defaults = {
        'method_number_percent': 20,
        'method_time': 'percent',
    }

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        res = super(account_asset_asset, self).onchange_category_id(
            cr, uid, ids, category_id, context=context)
        if category_id:
            category_obj = self.pool['account.asset.category'].browse(
                cr, uid, category_id, context=context)
            res['value'].update({
                'method_number': category_obj.method_number or '',
                'method_number_percent': category_obj.method_number_percent \
                or '',
                'first_year_half_rata': category_obj.first_year_half_rata,
            })
        return res

    def onchange_method_time(self, cr, uid, ids,
                             method_time='number', context=None):
        res = super(account_asset_asset, self).onchange_method_time(cr, uid, ids,
            method_time=method_time, context=context)
        if method_time == 'percent':
            res['value'].update({'prorata': False})
        return res

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        if 'method_time' in vals:
            if vals.get('method_time') == 'percent' and not vals.get('prorata'):
                vals['prorata'] = False
        return super(account_asset_asset, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        if 'method_time' in vals:
            if vals.get('method_time') == 'percent' and not vals.get('prorata'):
                vals['prorata'] = False
        for asset in self.browse(cr, uid, ids, context):
            asset_type = vals.get('type') or asset.type
            super(account_asset_asset, self).write(
                cr, uid, [asset.id], vals, context)
            if asset_type == 'view' or \
                    context.get('asset_validate_from_write'):
                continue
            #new
            if asset.type == 'normal' and context.get('update_asset_value_from_move_line'):
                # create asset variation line
                asset_line_obj = self.pool.get('account.asset.depreciation.line')
                line_name = self._get_depreciation_entry_name(cr, uid, asset, 0, context=context)
                asset_line_vals = {
                    'amount': context.get('asset_value'),
                    'asset_id': asset.id,
                    'name': line_name,
                    'line_date': asset.date_start,
                    'init_entry': True,
                    'type': 'create',
                }
                asset_line_id = asset_line_obj.create(cr, uid, asset_line_vals, context=context)
                asset_line_obj.write(cr, uid, [asset_line_id], {'move_id': context['move_id']})
        return True


class account_asset_depreciation_line(orm.Model):
    _inherit = 'account.asset.depreciation.line'
    _columns = {
        'parent_category_id': fields.related(
            'asset_id', 'category_id', type='many2one', string="Category of Asset"),
        'type': fields.selection([
            ('create', 'Asset Value'),
            ('depreciate', 'Depreciation'),
            ('remove', 'Asset Removal'),
            ], 'Type', readonly=False),
        'active': fields.boolean('Active')
    }

    def unlink(self, cr, uid, ids, context=None):
        for dl in self.browse(cr, uid, ids, context):
            if dl.type == 'create' and not context.get('remove_asset_dl_from_invoice', False):
                raise orm.except_orm(
                    _('Error!'),
                    _("You cannot remove an asset line "
                      "of type 'Asset Value'."))
            else:
                return super(account_asset_depreciation_line, self).unlink(
                    cr, uid, ids, context=context)

    def reload_page(self, cr, uid, asset_id, context=None):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def create_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            asset = line.asset_id
            if asset.method_time == 'year' \
                    or asset.method_time == 'percent':
                depreciation_date = context.get('depreciation_date') or \
                    line.line_date
            else:
                depreciation_date = context.get('depreciation_date') or \
                    time.strftime('%Y-%m-%d')
            ctx = dict(context, account_period_prefer_normal=True)
            period_ids = period_obj.find(
                cr, uid, depreciation_date, context=ctx)
            asset_name = asset.name
            reference = line.name
            journal_id = asset.category_id.journal_id.id
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            if context.get('create_move_from_button', False):
                ctx = {'allow_asset': True, 'create_move_from_button': True}
            #TODO in case of create_move not from invoice, deactivate subsequent purchase of asset
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': asset.category_id.account_depreciation_id.id,
                'debit': line.amount < 0 and -line.amount or 0.0,
                'credit': line.amount > 0 and line.amount or 0.0,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'date': depreciation_date,
                'asset_id': asset.id,
                'subsequent_asset': False,
            }, context=ctx)
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': asset.category_id.account_expense_depreciation_id.id,
                'credit': line.amount < 0 and -line.amount or 0.0,
                'debit': line.amount > 0 and line.amount or 0.0,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'analytic_account_id': asset.account_analytic_id.id or asset.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': asset.id,
                'subsequent_asset': False,
            }, context=ctx)
            self.write(cr, uid, line.id, {'move_id': move_id}, context={'allow_asset_line_update': True})
            created_move_ids.append(move_id)
            asset_ids.append(asset.id)
        # we re-evaluate the assets to determine whether we can close them
        for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
            if currency_obj.is_zero(cr, uid, asset.company_id.currency_id, asset.value_residual):
                asset.write({'state': 'close'})
            if len(ids) == 1 and context.get('create_move_from_button'):
                self.reload_page(cr, uid, asset.id, context)
        return created_move_ids

    def unlink_move(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if len(ids) == 1:
                self.reload_page(cr, uid, line.asset_id.id, context)
        return super(account_asset_depreciation_line, self).unlink_move(cr, uid, ids, context=context)


class account_asset_history(orm.Model):
    _inherit = 'account.asset.history'

    _columns = {
        'method_time': fields.selection([
            ('year', 'Number of Years'),
            ('percent', 'Percent'),
            ], 'Time Method', required=True,
            help="Choose the method to use to compute the dates and number of depreciation lines.\n"\
                 "  * Number of Years: Specify the number of years for the depreciation.\n" \
                 "  * Number of Depreciations: Fix the number of depreciation lines and the"
                 " time between 2 depreciations.\n" \
                 "  * Ending Date: Choose the time between 2 depreciations and the date the "
                 "depreciations won't go beyond."\
                 "  * Percent: Percentage depreciation per period (e.g. 25 = 25%)."),
        'method_number': fields.integer('Number of Depreciations/Years - method Number or Year.',
            help='The number of depreciations/years needed to depreciate your asset in method ' \
            'Number or Year.'),
        'method_number_percent': fields.float(' Percentage Depreciation - method Percent.',
            help='Percentage depreciation in method Percent.'),
    }