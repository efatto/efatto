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
            # if there is moves linked to the asset we have to delete
            # the linked depreciation lines to not leave orphans
            if adl_ids:
                    adl_obj.unlink(cr, uid, adl_ids, context={'remove_asset_dl_from_invoice': True})
        return True

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(
            cr, uid, x, part, date, context=context)
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
        if line.asset_id:
            res['asset_id'] = line.asset_id.id
        return res
