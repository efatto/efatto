# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Picking(models.Model):
    _inherit = "stock.picking"

    date_ready_to_deliver = fields.Datetime(
        compute='_compute_date_ready_to_deliver',
        store=True
    )

    @api.depends('state')
    def _compute_date_ready_to_deliver(self):
        for pick in self:
            if pick.state in ['draft', 'waiting', 'confirmed', 'cancel']:
                pick.date_ready_to_deliver = False
            elif pick.state == 'assigned':
                pick.date_ready_to_deliver = fields.Datetime.now()
