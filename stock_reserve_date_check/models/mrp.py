# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    enable_reserve_date_check = fields.Boolean(
        help="Forbid reservation on not possible date",
        copy=False)

    @api.multi
    def action_assign(self):
        # Add variable in context to enable check
        for production in self:
            if 'enable_reserve_date_check' in self.env.context:
                enable_reserve_date_check = self._context['enable_reserve_date_check']
            else:
                enable_reserve_date_check = production.enable_reserve_date_check
            super(MrpProduction, self.with_context(
                enable_reserve_date_check=enable_reserve_date_check
            )).action_assign()
        return True

    @api.onchange('date_planned_start', 'enable_reserve_date_check', 'availability')
    def _onchange_date_planned_start(self):
        if self.enable_reserve_date_check and self.availability in [
                'assigned', 'none']:
            # exclude new and running production from check
            if self._origin.id and not isinstance(self._origin.id, models.NewId):
                if self.state == 'confirmed' \
                        and self.date_planned_start < self._origin.date_planned_start:
                    raise UserError(_(
                        'Planned date start cannot be previous than planned!\n'
                        'To change it, unreserve the production, change the date '
                        'planned start and re-reserve, to ensure the reservation '
                        'is done with the new date.'))
