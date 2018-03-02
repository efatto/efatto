# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_cancel(self):
        for invoice in self:
            # we get move_lines with date_maturity and check if they are
            # present in some riba_distinta_line
            move_line_model = self.env['account.move.line']
            rdml_model = self.env['riba.distinta.move.line']
            move_line_ids = move_line_model.search([
                ('move_id', '=', invoice.move_id.id),
                ('date_maturity', '!=', False)])
            if move_line_ids:
                riba_line_ids = rdml_model.search(
                    [('move_line_id', 'in', [m.id for m in move_line_ids])])
                if riba_line_ids:
                    if len(riba_line_ids) > 1:
                        riba_line_ids = riba_line_ids[0]
                    # print(
                    #     _('Attention!'),
                    #     _('Invoice is linked to RI.BA. list nr {riba}. '
                    #       'You have to manually add link to riba.').format(
                    #         riba=riba_line_ids.riba_line_id.distinta_id.name
                    #     ))
                riba_line_ids.write({'move_line_id': False})
        super(AccountInvoice, self).action_cancel()