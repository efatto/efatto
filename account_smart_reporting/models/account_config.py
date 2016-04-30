# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountConfigSettings(models.TransientModel):

    _inherit = 'account.config.settings'

    accountant_partner_id = fields.Many2one(
        related='company_id.accountant_partner_id',
        help='Default Accountant partner',
        domain=[('supplier', '=', True)])

    def default_get(self, cr, uid, fields, context=None):
        res = super(AccountConfigSettings, self).default_get(
            cr, uid, fields, context)
        if res:
            user = self.pool['res.users'].browse(cr, uid, uid, context)
            res['due_cost_service_id'] = user.company_id.accountant_partner_id.id
        return res


class ResCompany(models.Model):

    _inherit = 'res.company'

    accountant_partner_id = fields.Many2one('res.partner')
