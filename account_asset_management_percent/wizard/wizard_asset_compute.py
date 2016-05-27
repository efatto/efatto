# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import fields, orm
from openerp.tools.translate import _


class asset_depreciation_confirmation_wizard(orm.TransientModel):
    _inherit = "asset.depreciation.confirmation.wizard"

    def asset_set_init(self, cr, uid, ids, context):
        ass_obj = self.pool.get('account.asset.asset')
        asset_ids = ass_obj.search(cr, uid, [('state', '=', 'open'),
                                             ('type', '=', 'normal')],
                                   context=context)
        data = self.browse(cr, uid, ids, context=context)
        asset_board_obj = self.pool['account.asset.depreciation.line']
        period_id = data[0].period_id.id
        period = self.pool['account.period'].browse(
            cr, uid, period_id, context)
        init_move_ids = []
        for asset in ass_obj.browse(cr, uid, asset_ids, context):
            if not asset_board_obj.search(cr, uid, [
                    ('asset_id', '=', asset.id),
                    ('move_id', '!=', False),
                    ('type', '=', 'depreciate')]):
                asset_board_moves = asset_board_obj.search(cr, uid, [
                    ('asset_id', '=', asset.id),
                    ('line_date', '=', period.date_stop),
                    ('move_id', '=', False)])
                for asset_board in asset_board_obj.browse(
                        cr, uid, asset_board_moves, context):
                    asset_board.write({'init_entry': True})
                    init_move_ids.append(asset_board.id)
        return {
            'name': _('Asset Moves Confirmed as Init entry'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.depreciation.line',
            'view_id': False,
            'domain': "[('id','in',[" + ','.join(
                map(str, init_move_ids)) + "])]",
            'type': 'ir.actions.act_window',
        }
