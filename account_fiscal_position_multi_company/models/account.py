# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.v7
    def map_tax(self, cr, uid, fposition_id, taxes, context=None):
        if not taxes:
            return []
        user = self.pool.get('res.users').browse(cr, uid, uid,
                                                 context=context)
        if user.company_id:
            company_id = user.company_id
        if not fposition_id:
            return map(lambda x: x.id, [tax for tax in taxes if
                                        tax.company_id == company_id])

        result = set()
        for t in taxes:
            ok = False
            for tax in fposition_id.tax_ids:
                if tax.tax_src_id.id == t.id and \
                        tax.tax_dest_id.company_id == company_id:
                    if tax.tax_dest_id:
                        result.add(tax.tax_dest_id.id)
                    ok = True
            if not ok:
                if t.company_id == company_id:
                    result.add(t.id)
        return list(result)

    @api.v8
    def map_tax(self, taxes):
        result = self.env['account.tax'].browse()
        for tax in taxes:
            tax_count = 0
            for t in self.tax_ids:
                if t.tax_src_id == tax:
                    tax_count += 1
                    if t.tax_dest_id and \
                            t.tax_dest_id.company_id == \
                            self.env.user.company_id:
                        result |= t.tax_dest_id
            if not tax_count and tax.company_id == self.env.user.company_id:
                result |= tax
        return result
