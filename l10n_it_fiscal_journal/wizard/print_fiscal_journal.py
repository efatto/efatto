# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class WizardFiscalJournal(models.TransientModel):

    @api.model
    def _get_period(self):
        ctx = dict(self._context or {}, account_period_prefer_normal=True)
        period_ids = self.env[
            'account.period'].with_context(context=ctx).find()
        return period_ids

    _name = "wizard.fiscal.journal"
    _rec_name = "type"

    period_ids = fields.Many2many(
        'account.period',
        'fiscal_journal_periods_rel',
        'period_id',
        'registro_id',
        string='Periods',
        default=_get_period,
        help='Select periods you want retrieve documents from',
        required=True)
    type = fields.Selection([
        ('fiscal_journal', 'Libro Giornale'),
        ], 'Layout', required=True,
        default='fiscal_journal')
    journal_ids = fields.Many2many(
        'account.journal',
        'fiscal_journal_journals_rel',
        'journal_id',
        'fiscal_journal_id',
        string='Journals',
        help='Select journals you want retrieve documents from',
        required=True)
    message = fields.Char(string='Message', size=64, readonly=True)
    fiscal_page_base = fields.Integer('Last printed page', required=True)

    @api.multi
    def print_journal(self):
        self.ensure_one()
        move_obj = self.env['account.move']
        move_ids = move_obj.search([
            ('journal_id', 'in', [j.id for j in self.journal_ids]),
            ('period_id', 'in', [p.id for p in self.period_ids]),
            ('state', '=', 'posted'),
            ], order='date, name')
        if not move_ids:
            raise UserError(_('No documents found in the current selection'))
        datas_form = {}
        datas_form['period_ids'] = [p.id for p in self.period_ids]
        datas_form['journal_ids'] = [j.id for j in self.journal_ids]
        datas_form['fiscal_page_base'] = self.fiscal_page_base
        report_name = 'l10n_it_fiscal_journal.report_fiscal_journal'
        datas = {
            'ids': [m.id for m in move_ids],
            'model': 'account.move',
            'form': datas_form,
        }
        return self.env['report'].get_action(self, report_name, data=datas)
