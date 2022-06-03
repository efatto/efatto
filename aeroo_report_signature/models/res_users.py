# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    signature_logo = fields.Binary(
        string="Image for signature",
        help="Set image for signature on reports",
    )
