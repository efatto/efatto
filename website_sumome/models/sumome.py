# -*- coding: utf-8 -*-
from openerp import models,fields

class Website(models.Model):

    _inherit = "website"

    sumome_site_id = fields.Char(
        'SumoMe Site Id', help='The SumoMe site id is  available at www.sumome.com',size=128) 
