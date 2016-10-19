# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.multi
    @api.depends('fiscal_position')
    def map_tax(self, taxes):
        result = self.env['account.tax'].browse()
        for tax in taxes:
            tax_count = 0
            for t in self.tax_ids:
                if t.tax_src_id == tax:
                    tax_count += 1
                    if t.tax_dest_id and \
                            t.tax_dest_id.company_id == self.user.company_id:
                        result |= t.tax_dest_id
            if not tax_count and tax.company_id == self and self.user.company_id:
                result |= tax
        return result
