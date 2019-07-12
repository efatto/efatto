# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _compute_analytic(self, domain=None):
        super(SaleOrderLine, self)._compute_analytic(domain=domain)
        self.env.ref('product.product_uom_categ_unit')
        project_task_model = self.env['project.task']
        for line in self:
            if line.product_id.invoice_policy == 'order' and \
                    line.product_uom.category_id == self.env.ref(
                        'product.product_uom_categ_unit'):
                # le ore pianificate sono la somma di tutti i task esclusi
                # quelli collegati alle singole righe
                project_fetch_data = project_task_model.read_group(
                    [('project_id', 'in',
                      line.order_id.sudo().related_project_id.project_ids.ids)],
                    ['planned_hours', 'sale_line_id'], ['sale_line_id'],
                )
                for line_data in project_fetch_data:
                    if line_data.get('sale_line_id'):
                        if line_data['sale_line_id'][0] == line.id:
                            hours_planned = line_data['planned_hours'] or 0.0
                            break
                    else:
                        hours_planned = line_data['planned_hours'] or 0.0
                line.qty_delivered = line.qty_delivered / hours_planned
        return True
