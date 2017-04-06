# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields
from openerp.addons.base.res.res_partner import format_address


class ResPartner(models.Model, format_address):
    _inherit = "res.partner"

    company_id = fields.Many2one(default=False)
