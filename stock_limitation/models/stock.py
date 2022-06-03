# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class stock_location(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many('res.users','stock_location_users_rel','slid','user_id','Accepted Users')