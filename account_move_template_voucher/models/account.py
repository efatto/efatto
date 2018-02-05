# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    template_id = fields.Many2one(
        'account.move.template', 'Account Move Template', )

    @api.onchange('template_id')
    def onchange_template_id(self):
        if not self.template_id:
            return
        if self.template_id.cross_journals:
            raise exceptions.Warning(_("Error! Not possible in more than one "
                                       "journal. Create from wizard"))
        if self.template_id.journal_id:
            self.journal_id = self.template_id.journal_id
        elif self.template_id.template_line_ids:
            if self.template_id.template_line_ids[0].journal_id:
                self.journal_id = self.template_id.template_line_ids[
                    0].journal_id
