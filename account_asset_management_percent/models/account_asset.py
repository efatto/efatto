# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime
from decimal import Decimal, ROUND_UP
from openerp.tools.translate import _


class AccountAssetCategory(orm.Model):
    _inherit = 'account.asset.category'

    def _compute_year_from_percent(
            self, cr, uid, ids, field_name, arg, context):
        res = {}
        for category in self.browse(cr, uid, ids):
            res[category.id] = 100.0 / (category.method_percent and
                                     category.method_percent or 100.0)
        return res

    def _get_method_time(self, cr, uid, context=None):
        super(AccountAssetCategory, self)._get_method_time(
            cr, uid, context=context)
        return [
            ('year', _('Percent')),
        ]

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
        dl_ids = asset.depreciation_line_ids
        depreciated_amount = 0.0
        depreciated_year = 0
        if asset.first_year_half:
            lost_years = 1
        else:
            lost_years = 0

        if dl_ids:
            for dl in dl_ids:
                if dl.type == 'depreciate':
                    depreciated_amount += dl.amount
                    depreciated_year += 1
            if depreciated_year > 0:
                standard_depreciation_amount = asset.asset_value * \
                                               asset.method_percent / 100.0
                diff = standard_depreciation_amount * \
                       depreciated_year - depreciated_amount
                if diff != 0:
                    lost_years = int(Decimal(str(
                        diff / standard_depreciation_amount)).quantize(
                        Decimal('0')))
                #lost_years = int(Decimal(str(initial_depreciation_lines - initial_depreciation_amount / (standard_depreciation_amount))).quantize(Decimal('0'), rounding=ROUND_UP))

        if asset.method_time == 'year':
            depreciation_stop_date = depreciation_start_date + \
                relativedelta(
                    years=(int(asset.method_number) + lost_years), days=-1)
        return depreciation_stop_date

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        super(AccountAssetAsset, self).compute_depreciation_board(
            cr, uid, ids, context)
        adl_obj = self.pool['account.asset.depreciation.line']
        depreciation_lin_obj = self.pool.get(
            'account.asset.depreciation.line')
        for asset in self.browse(cr, uid, ids, context):
            depreciation_start_line_id = adl_obj.search(
                cr, uid, [
                    ('asset_id', '=', asset.id), ('type', '=', 'depreciate'),
                ], order='line_date asc', limit=1)
            if depreciation_start_line_id:
                depreciation_start_date = adl_obj.browse(
                    cr, uid, depreciation_start_line_id, context
                    )[0].line_date[:4] + '-01-01'
                last_depreciation_id = adl_obj.search(
                    cr, uid, [('asset_id', '=', asset.id),
                              ('type', '=', 'depreciate'),
                              ], order='line_date desc', limit=1)
                if last_depreciation_id:
                    adl = adl_obj.browse(cr, uid, last_depreciation_id, context)[0]
                    last_depreciation_date = datetime.strptime(
                        (adl.line_date), '%Y-%m-%d')
                depreciation_stop_date = self._get_depreciation_stop_date(
                    cr, uid, asset, datetime.strptime(
                        depreciation_start_date, '%Y-%m-%d'), context)
                if depreciation_stop_date > last_depreciation_date:
                    vals = {
                        'previous_id': adl.id,
                        'amount': adl.amount,
                        'asset_id': asset.id,
                        'name': adl.name,
                        'line_date': adl.line_date,
                        #TODO .strftime('%Y-%m-%d'), # mettere l'anno successivo
                    }
                    depr_line_id = depreciation_lin_obj.create(
                        cr, uid, vals, context=context)
                    depreciation_lin_obj.write(
                        cr, uid, last_depreciation_id, {}, context=context)

    def _compute_year_amount(self, cr, uid, asset, amount_to_depr,
                             residual_amount, context=None):
        if asset.method_time == 'year':
            year_amount_linear = amount_to_depr * asset.method_percent / 100.0
            if asset.first_year_half:
                if residual_amount == amount_to_depr:
                    year_amount_linear = amount_to_depr * \
                                         asset.method_percent / 100.0 / 2.0
            if residual_amount < year_amount_linear:
                year_amount_linear = residual_amount

        return year_amount_linear

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        res = super(AccountAssetAsset, self).onchange_category_id(
            cr, uid, ids, category_id, context=context)
        asset_categ_obj = self.pool.get('account.asset.category')
        if category_id:
            category_obj = asset_categ_obj.browse(
                cr, uid, category_id, context=context)
            res['value'].update({
                'method_percent': category_obj.method_percent,
                'first_year_half': category_obj.first_year_half,
            })
        return res


class AccountAssetDepreciationLine(orm.Model):
    _inherit = 'account.asset.depreciation.line'

    _columns = {
        'parent_category_id': fields.related(
            'asset_id', 'category_id', type='many2one',
            relation='account.asset.category', string="Category of Asset"),
        'type': fields.selection([
            ('create', 'Asset Value Create'),
            ('purchase', 'Asset Value Purchase'),
            ('sell', 'Asset Value Sale'),
            ('depreciate', 'Depreciation'),
            ('remove', 'Asset Removal'),
        ], 'Type', readonly=False
        ),
        'active': fields.boolean('Active')
    }
    _defaults = {
        'active': True,
    }

