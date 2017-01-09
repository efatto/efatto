# -*- coding: utf-8 -*-
from openerp import models, fields


class ir_model(models.Model):
    _inherit = 'ir.model'

    email_organizer = fields.Boolean('Use in Email Organizer')
