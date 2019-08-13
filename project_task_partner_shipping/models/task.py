# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    partner_shipping_id = fields.Many2one(
        'res.partner', 'Delivery Address',
        domain="[('parent_id', '=', partner_id)]",
        help="Delivery address for current task.")
