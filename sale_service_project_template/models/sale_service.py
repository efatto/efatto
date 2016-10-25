# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _is_procurement_project(self, procurement):
        return procurement.product_id.type == 'service' and \
               procurement.product_id.project_template_id or False

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if not res:
            #if there isn't any specific procurement.rule defined for the
            #  product, we may want to create a project
            if self._is_procurement_project(procurement):
                return True
        return res

    @api.model
    def _prepare_project(self, procurement):
        sale_order = procurement.sale_line_id.order_id
        res = {
            'user_id': sale_order.user_id.id,
            'name': sale_order.name,
            'partner_id': sale_order.partner_id.id,
            'pricelist_id': sale_order.pricelist_id.id,
            'invoice_on_timesheets': sale_order.invoice_on_timesheets,
        }
        return res

    @api.model
    def _get_project(self, procurement):
        order = procurement.sale_line_id.order_id
        if order.project_id:
            parent = order.project_id
        # search if partner has an analytic account
        else:
            parent_id = self.env['project.project'].search(
                [('partner_id', '=',
                  procurement.sale_line_id.order_id.partner_id.id)], limit=1)
            if parent_id:
                parent = self.env['project.project'].browse(parent_id.id)

        if parent and order.name in parent.name:
            project = self.env['project.project'].search(
                [('analytic_account_id', '=', parent.id)])
        else:
            vals = self._prepare_project(procurement)
            if parent:
                vals.update({
                    'parent_id': parent.id,
                    'to_invoice': parent.to_invoice.id,
                })
            if not parent.to_invoice and order.invoice_on_timesheets:
                vals['to_invoice'] = self.env.ref(
                    'hr_timesheet_invoice.timesheet_invoice_factor1').id
            project = self.env['project.project'].create(vals)
            order.project_id = project.analytic_account_id.id
        return project

    @api.model
    def _create_project(self, procurement):
        project = self._get_project(procurement)
        order = procurement.sale_line_id.order_id
        # set project created from template as child of analytic account
        # create project from template if selected
        for product in procurement.sale_line_id.product_id:
            if product.project_template_id:
                for task in self.env['project.task'].search(
                        [('project_id', '=', product.project_template_id.id),
                         ('active', '=', False)],):
                    new_task = task.copy(default={
                        'name': ': '.join([order.name, task.name, ]),
                        'project_id': project.id,
                        'date_start': fields.Date.today(),
                    })
                    new_task.parent_ids += self.parent_task_id
                # remove template project delegation from created tasks
                for task in self.env['project.task'].search(
                    [('project_id', '=', product.project_template_id.id)]):
                    for parent_task in task.parent_ids:
                        if parent_task.project_id == \
                                product.project_template_id:
                            task.parent_ids -= parent_task
                    for child_task in task.child_ids:
                        if child_task.project_id == \
                                product.project_template_id:
                            task.child_ids -= child_task
        return project

    @api.model
    def _run(self, procurement):
        if self._is_procurement_project(procurement):
            # and not procurement.task_id: ?
            # create a task for the procurement
            return self._create_project(procurement)
        return super(ProcurementOrder, self)._run(procurement)
