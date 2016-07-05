# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProjectTaskMaterials(models.Model):
    _inherit = "project.task.materials"

    amount_unit = fields.Float(string='Cost')
    amount_total = fields.Float(string='Cost Total')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(ProjectTaskMaterials, self)._onchange_product_id()
        analytic_line_obj = self.pool.get('account.analytic.line')
        company_id = self.env['res.company']._company_default_get(
            'account.analytic.line')
        journal = self.env.ref(
            'project_task_materials_stock.analytic_journal_sale_materials')
        amount_dic = analytic_line_obj.on_change_unit_amount(
            self._cr, self._uid, self._ids, self.product_id.id,
            self.uos_qty() != 0.0 and self.uos_qty() or 1,
            company_id, False, journal.id, self._context)
        if amount_dic:
            if amount_dic.get('value', False).get('amount', False):
                if self.quantity != 0:
                    self.amount_unit = - amount_dic['value']['amount'] / \
                                       self.quantity
                    self.amount_total = - amount_dic['value']['amount']
                else:
                    self.amount_unit = - amount_dic['value']['amount']
        return res

    @api.onchange('quantity')
    @api.depends('amount_unit')
    def _onchange_quantity(self):
        self.amount_total = self.amount_unit * self.quantity
