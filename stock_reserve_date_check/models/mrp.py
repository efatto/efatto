# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    enable_reserve_date_check = fields.Boolean(
        help="Forbid reservation on not possible date",
        default=True, copy=False)

    @api.multi
    def action_assign(self):
        # Add variable in context to enable check
        for production in self:
            super(MrpProduction, self.with_context(
                enable_reserve_date_check=production.enable_reserve_date_check
            )).action_assign()
        return True

    @api.onchange('date_planned_start', 'enable_reserve_date_check', 'availability')
    def _onchange_date_planned_start(self):
        if self.enable_reserve_date_check and self.availability in [
                'assigned', 'none']:
            if self.date_planned_start < self._origin.date_planned_start:
                raise UserError(_(
                    'Planned date start cannot be previous than planned!\n'
                    'To change it, unreserve the production, change date'
                    'planned start and re-reserve, to ensure reservation'
                    'is done with the new date.'))
