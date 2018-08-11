# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    partner_shipping_id = fields.Many2one(
        'res.partner', 'Delivery Address',
        domain="[('parent_id', '=', partner_id)]",
        help="Delivery address for current task.")
