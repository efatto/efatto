# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    create_ddt = fields.Boolean(string='Automatically create the DDT')


class StockConfigSettingsDDT(models.TransientModel):
    _inherit = 'stock.config.settings'

    create_ddt = fields.Boolean(
        string="Automatically create the DDT",
        related='company_id.create_ddt')

    @api.model
    def default_get(self, fields):
        res = super(StockConfigSettingsDDT, self).default_get(fields)
        if res:
            company = self.env.user.company_id
            res['create_ddt'] = company.create_ddt \
                if company.create_ddt else False
        return res
