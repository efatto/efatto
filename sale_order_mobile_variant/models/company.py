# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_mobile_partner_default = fields.Many2one(
        comodel_name='res.partner',
        company_dependent=True,)
