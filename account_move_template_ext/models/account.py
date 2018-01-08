# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class AccountMove(models.Model):
    _inherit = "account.move"

    template_id = fields.Many2one(
        'account.move.template', 'Account Move Template',)

    @api.onchange('template_id')
    def onchange_template_id(self):
        if not self.template_id:
            return
        if self.template_id.cross_journals:
            raise exceptions.Warning(_("Error! Not possible in more than one "
                                       "journal. Create from wizard"))
        if self.template_id.template_line_ids:
            if self.template_id.template_line_ids[0].journal_id:
                self.journal_id = self.template_id.template_line_ids[
                    0].journal_id
        if not self.journal_id:
            return
        lines = []
        for line in self.template_id.template_line_ids:
            analytic_account_id = False
            if line.analytic_account_id:
                if not line.journal_id.analytic_journal_id:
                    raise exceptions.Warning(
                        _("You have to define an analytic "
                          "journal on the '%s' journal!")
                        % (line.journal_id.name,)
                    )
                analytic_account_id = line.analytic_account_id.id
            lines.append({
                'name': line.name,
                'journal_id': self.journal_id.id,
                'period_id': self.period_id.id,
                'analytic_account_id': analytic_account_id,
                'account_id': line.account_id.id,
                'date': self.date,
                'account_tax_id': line.account_tax_id.id,
                'credit': line.move_line_type == 'cr' and (
                    line.type == 'amount' and line.amount or 1.0) or 0.0,
                'debit': line.move_line_type == 'dr' and (
                    line.type == 'amount' and line.amount or 1.0) or 0.0,
            })
        self.line_id = lines
