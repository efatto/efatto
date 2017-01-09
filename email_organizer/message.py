# -*- coding: utf-8 -*-
from openerp import models, fields


class mail_message(models.Model):
    _inherit = 'mail.message'

    name = fields.Char('Name')
