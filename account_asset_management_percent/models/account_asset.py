# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime
from decimal import Decimal, ROUND_UP


class AccountAssetCategory(orm.Model):
    _inherit = 'account.asset.category'

    def _compute_year_from_percent(
            self, cr, uid, ids, field_name, arg, context):
        res = {}
        for category in self.browse(cr, uid, ids):
            res[category.id] = 100.0 / (category.method_percent and
                                     category.method_percent or 100.0)
        return res

    _columns = {
        'method_number': fields.function(
            _compute_year_from_percent,
            method=True, readonly=False,
            string='Number of Years'),
        'method_percent': fields.float(
            'Percentage Depreciation',
            readonly=False,
            help="Percentage depreciation."),
        'first_year_half': fields.boolean(
            'First Year 50%',
            help='The first depreciation entry will be computed at 50%.'),
    }


class AccountAssetAsset(orm.Model):
    _inherit = 'account.asset.asset'

    def _compute_year_from_percent(
            self, cr, uid, ids, field_name, arg, context):
        res = {}
        for asset in self.browse(cr, uid, ids):
            res[asset.id] = 100.0 / (asset.method_percent and
                                     asset.method_percent or 100.0)
        return res

    _columns = {
        'method_number': fields.function(
            _compute_year_from_percent, method=True, readonly=True,
            string='Number of Years'),
        'method_percent': fields.float(
            'Percentage Depreciation',
            readonly=True, states={'draft': [('readonly', False)]},
            help="Percentage depreciation."),
        'first_year_half': fields.boolean(
            'First Year 50%',
            help='The first depreciation entry will be computed at 50%.'),
    }

    def _get_depreciation_stop_date(self, cr, uid, asset,
                                    depreciation_start_date, context=None):
        if asset.method_time == 'year':
            depreciation_stop_date = depreciation_start_date + \
                relativedelta(years=int(Decimal(asset.method_number).quantize(Decimal('1'), rounding=ROUND_UP)), days=-1)
        # elif asset.method_time == 'number':
        #     if asset.method_period == 'month':
        #         depreciation_stop_date = depreciation_start_date + \
        #             relativedelta(months=asset.method_number, days=-1)
        #     elif asset.method_period == 'quarter':
        #         depreciation_stop_date = depreciation_start_date + \
        #             relativedelta(months=asset.method_number * 3, days=-1)
        #     elif asset.method_period == 'year':
        #         depreciation_stop_date = depreciation_start_date + \
        #             relativedelta(years=asset.method_number, days=-1)
        # elif asset.method_time == 'end':
        #     depreciation_stop_date = datetime.strptime(
        #         asset.method_end, '%Y-%m-%d')
        return depreciation_stop_date

#
#
# class account_asset_depreciation_line(orm.Model):
#     _inherit = 'account.asset.depreciation.line'
#     _columns = {
#         'parent_category_id': fields.related(
#             'asset_id', 'category_id', type='many2one',
#             relation='account.asset.category', string="Category of Asset"),
#         'type': fields.selection([
#             ('create', 'Asset Value'),
#             ('purchase', 'Asset Value'),
#             ('sell', 'Asset Value'),
#             ('depreciate', 'Depreciation'),
#             ('remove', 'Asset Removal'),
#         ], 'Type', readonly=False
#         ),
#         'active': fields.boolean('Active')
#     }
#     _defaults = {
#         'active': True,
#     }

