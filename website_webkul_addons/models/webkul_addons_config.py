# -*- coding = utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https =//webkul.com/>)
#   See LICENSE file for full copyright and licensign details.
#################################################################################

from openerp import api, fields, models, _
from openerp.exceptions import Warning

class WebkulWebsiteAddons(models.TransientModel):
    _name = 'webkul.website.addons'
    _inherit = 'res.config.settings'

    #Website SEO
    module_website_seo = fields.Boolean(string = "Website: SEO")
