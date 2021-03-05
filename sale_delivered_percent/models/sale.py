# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('analytic_line_ids.project_id',
                 'analytic_line_ids.project_id.task_ids',
                 'analytic_line_ids.project_id.task_ids.planned_hours')
    def _compute_qty_delivered(self):
        """
        Function to correct the display of the delivered quantity on
        sales lines with invoicing on 'ordered' and with unit of measure 'units':
        instead of adding the hours worked, it calculates the % of hours worked
        on the hours foreseen in the single tasks.
        """
        super(SaleOrderLine, self)._compute_qty_delivered()
        for line in self:
            if line.product_id.invoice_policy == 'order' and \
                    line.product_uom.category_id == self.env.ref(
                        'uom.product_uom_categ_unit'):
                # le ore pianificate sono la somma delle ore pianificate
                # di tutti i task esclusi quelli collegati alle singole righe
                hours_planned = 0.0
                project_fetch_data = self.env['project.task'].read_group(
                    [('project_id', 'in', line.order_id.sudo(
                        ).project_ids.ids)],
                    ['planned_hours', 'sale_line_id'], ['sale_line_id'],
                )
                for line_data in project_fetch_data:
                    if line_data.get('sale_line_id'):
                        if line_data['sale_line_id'][0] == line.id:
                            hours_planned = line_data['planned_hours'] or 0.0
                            break
                    else:
                        hours_planned = line_data['planned_hours'] or 0.0
                if hours_planned != 0.0:
                    line.qty_delivered = line.qty_delivered / hours_planned
                else:
                    line.qty_delivered = 0.0
