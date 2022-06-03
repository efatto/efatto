# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    brand_logo = fields.Binary(
        string="Image for branding logo",
        help="Set image on bottom of reports",
    )


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    brand_logo = fields.Binary(
        string="Image for branding logo",
        help="Set image on bottom of reports",
        related='company_id.brand_logo',
    )
