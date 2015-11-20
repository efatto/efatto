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


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, context=None):
        super(account_invoice, self).action_number(cr, uid, ids, context)
        asset_obj = self.pool['account.asset.asset']
        asset_line_obj = self.pool['account.asset.depreciation.line']
        for inv in self.browse(cr, uid, ids):
            for aml in inv.move_id.line_id:
                if aml.asset_id and not aml.subsequent_asset:
                    asset = aml.asset_id
                    ctx = {'create_asset_from_move_line': True}
                    asset_obj.write(
                        cr, uid, [asset.id],
                        {'code': '', }, context=ctx)
                    # TODO progressive number?
                    asset_line_name = asset_obj._get_depreciation_entry_name(
                         cr, uid, asset, 0)
                    asset_line_obj.write(
                        cr, uid, [asset.depreciation_line_ids[0].id],
                        {'name': asset_line_name},
                        context={'allow_asset_line_update': True})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        assets = []
        for inv in self.browse(cr, uid, ids):
            move = inv.move_id
            assets = move and \
                [aml.asset_id for aml in
                 filter(lambda x: x.asset_id, move.line_id)]
        super(account_invoice, self).action_cancel(
            cr, uid, ids, context=context)
        if assets:
            adl_obj = self.pool['account.asset.depreciation.line']
            adl_ids = adl_obj.search(cr, uid, [('move_id', '=', move.id)])
            asset_obj = self.pool.get('account.asset.asset')
            for asset in asset_obj.browse(cr, uid, [x.id for x in assets]):
                # delete asset only if not invoice rows linked left
                if not asset.account_move_line_ids:
                    asset_obj.unlink(cr, uid, [x.id for x in assets])
                # if there is moves linked to the asset we have to delete
                # the linked depreciation lines for not leave orphans
                elif adl_ids:
                    adl_obj.unlink(cr, uid, adl_ids, context={'remove_asset_dl_from_invoice': True})
        return True

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(
            cr, uid, x, part, date, context=context)
        if x.get('asset_category_id'):
            # skip empty debit/credit
            if res.get('debit') or res.get('credit'):
                res['asset_category_id'] = x['asset_category_id']
        if x.get('asset_id'):
            if res.get('debit') or res.get('credit'):
                res['asset_id'] = x['asset_id']
        return res


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def onchange_asset_id(self, cr, uid, ids, asset_id):
        res = {}
        if asset_id:
            asset_id = self.pool['account.asset.asset'].browse(cr, uid, asset_id)
            res['value'] = {'asset_category_id': asset_id.category_id.id}
        return res

    def onchange_asset_ctg_id(self, cr, uid, ids, asset_ctg_id):
        res = {}
        if asset_ctg_id:
            asset_ctg = self.pool['account.asset.category'].browse(cr, uid, asset_ctg_id)
            res['value'] = {'account_id': asset_ctg.account_asset_id.id}
        return res

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(
            cr, uid, line, context)
        if line.asset_category_id:
            res['asset_category_id'] = line.asset_category_id.id
        if line.asset_id:
            res['asset_id'] = line.asset_id.id
        return res
