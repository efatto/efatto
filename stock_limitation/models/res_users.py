# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class res_users(models.Model):
    _inherit = 'res.users'

    location_ids = fields.Many2many('stock.location','stock_location_users_rel','user_id','slid','Accepted Location')