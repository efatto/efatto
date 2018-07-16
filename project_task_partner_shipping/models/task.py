# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, api, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    partner_shipping_id = fields.Many2one(
        'res.partner', 'Delivery Address',
        domain="[('parent_id', '=', partner_id)]",
        help="Delivery address for current task.")

    def onchange_user_id(self, cr, uid, ids, user_id, context=None):
        vals = {}
        # remove change of date_start when assigned
        # if user_id:
        #     vals['date_start'] = fields.datetime.now()
        return {'value': vals}
