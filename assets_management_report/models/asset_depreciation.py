# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AssetDepreciation(models.Model):
    _inherit = 'asset.depreciation'

    date_remove = fields.Date(compute='_compute_date_remove', store=True)

    @api.multi
    @api.depends('line_ids')
    def _compute_date_remove(self):
        for depr in self:
            date_remove = False
            if depr.line_ids:
                remove_line_ids = depr.line_ids.filtered(
                    lambda x: x.move_type == 'out'
                    and x.amount == depr.asset_id.purchase_amount)
                if remove_line_ids:
                    date_remove = remove_line_ids[0].date
            depr.date_remove = date_remove
