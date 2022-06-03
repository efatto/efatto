# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    sale_project_id = fields.Many2one(
        'project.project', 'Sale project', copy=False)

    @api.model
    def _is_procurement_project(self, procurement):
        return procurement.product_id.type == 'service' and \
               procurement.product_id.project_template_id or False

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if not res:
            #  if there isn't any specific procurement.rule defined for the
            #  product, we may want to create a project
            if self._is_procurement_project(procurement):
                return True
        return res

    @api.model
    def _create_service_project(self, procurement):
        # project_task = self.pool.get('project.task')
        project = self._get_project(procurement)
        project_dict = procurement.product_id.project_template_id.\
            duplicate_template()
        project_temp = self.env['project.project'].browse(
            project_dict.get('res_id'))
        for task in project_temp.task_ids:
            task.write({
                'partner_id': procurement.sale_line_id and
                procurement.sale_line_id.order_id.partner_id.id or
                procurement.partner_dest_id.id,
                'project_id': project.id,
                'company_id': procurement.company_id.id,
                'procurement_id': procurement.id,
                'date_deadline': procurement.date_planned,
            })
        project_temp.unlink()
        self.write({'sale_project_id': project.id})
        self.project_task_create_note()
        return project.task_ids[0]

    @api.model
    def _run(self, procurement):
        if self._is_procurement_project(procurement) \
                and not procurement.sale_project_id:
            # create a project for the procurement
            return self._create_service_project(procurement)
        return super(ProcurementOrder, self)._run(procurement)
