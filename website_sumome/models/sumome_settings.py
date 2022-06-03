# -*- coding: utf-8 -*-
from openerp import models,fields

class WebsiteConfigSettings(models.TransientModel):

    _inherit = "website.config.settings"

    sumome_site_id = fields.Char(
        related=['website_id', 'sumome_site_id'])
