# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _


class AssetDepreciationConfirmationWizard(models.TransientModel):
    _inherit = "asset.depreciation.confirmation.wizard"

    def _get_default_fiscalyear(self):
        fiscalyear_id = self.env['account.fiscalyear'].find()
        if fiscalyear_id:
            fy = self.env['account.fiscalyear'].browse(fiscalyear_id)
        return fy and fy or False

    set_init = fields.Boolean(
        'Set init',
        help='Set depreciation as init for current fiscal year.')
    fy_id = fields.Many2one(
        'account.fiscalyear', 'Fiscal Year',
        domain="[('state', '=', 'draft')]",
        default=_get_default_fiscalyear,
        required=True, help='Calculate depreciation table for asset acquired'
        ' in this Fiscal Year'
    )
    period_id = fields.Many2one(
        'account.period', 'Period',
        domain="[('special', '=', False), ('state', '=', 'draft')]",
        required=False,
        )

    @api.multi
    def asset_set_init(self):
        self.ensure_one()
        ass_obj = self.env['account.asset.asset']
        asset_ids = ass_obj.search([('state', 'in', ['open', 'draft']),
            ('type', '=', 'normal')])
        asset_board_obj = self.env['account.asset.depreciation.line']
        fy = self[0].fy_id
        set_init = self[0].set_init
        init_move_ids = []
        for asset in asset_ids:
            asset.compute_depreciation_board()
            if not asset_board_obj.search([
                    ('asset_id', '=', asset.id),
                    ('move_id', '!=', False),
                    ('type', '=', 'depreciate')]):
                asset_board_moves = asset_board_obj.search([
                    ('asset_id', '=', asset.id),
                    ('line_date', '>=', fy.date_start),
                    ('line_date', '<=', fy.date_stop),
                    ('move_id', '=', False)])
                for asset_board in asset_board_moves:
                    if set_init:
                        asset_board.init_entry = True
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
