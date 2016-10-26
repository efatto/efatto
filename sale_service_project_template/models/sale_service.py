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
            #if there isn't any specific procurement.rule defined for the
            #  product, we may want to create a project
            if self._is_procurement_project(procurement):
                return True
        return res

    @api.model
    def _create_service_task(self, procurement):
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
            })
        project_temp.unlink()
        #project.task_ids.partner_id = project.partner_id
        #project.task_ids.procurement_id = procurement.id
        # planned_hours = self._convert_qty_company_hours(cr, uid, procurement, context=context)
        # task_id = project_task.create(cr, uid, {
        #     'name': '%s:%s' % (procurement.origin or '', procurement.product_id.name),
        #     'date_deadline': procurement.date_planned,
        #     'planned_hours': planned_hours,
        #     'remaining_hours': planned_hours,
        #     'partner_id': procurement.sale_line_id and procurement.sale_line_id.order_id.partner_id.id or procurement.partner_dest_id.id,
        #     'user_id': procurement.product_id.product_manager.id,
        #     'procurement_id': procurement.id,
        #     'description': procurement.name + '\n',
        #     'project_id': project and project.id or False,
        #     'company_id': procurement.company_id.id,
        # },context=context)
        self.write({'sale_project_id': project.id})
        self.project_task_create_note()
        return project.task_ids[0]

    @api.model
    def _run(self, procurement):
        if self._is_procurement_project(procurement) \
                and not procurement.sale_project_id:
            # create a project for the procurement
            return self._create_service_task(procurement)
        return super(ProcurementOrder, self)._run(procurement)
