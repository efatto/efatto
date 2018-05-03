# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _, workflow
from openerp.exceptions import Warning as UserError
from openerp.addons.l10n_configurable.model.account import \
    PAYMENT_TERM_TYPE_SELECTION


class RibaUnsolved(models.TransientModel):
    _inherit = 'riba.unsolved'

    @api.model
    def _get_effects_amount(self):
        super(RibaUnsolved, self)._get_effects_amount()
        amount = 0
        for line in self.env['riba.distinta.line'].browse(
                self.env.context['active_ids']):
            amount += line.amount
        return amount

    new_due_date = fields.Date('New due date')
    new_payment_term_type = fields.Selection(
        PAYMENT_TERM_TYPE_SELECTION, "Type of payment")
    overdue_effects_amount = fields.Float(
        default=_get_effects_amount,
        string='Overdue Effects amount')

    @api.cr_uid_ids_context
    def create_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context and context.get('active_ids', False) or False
        if not active_ids:
            raise UserError(_('No active IDs found'))
        move_pool = self.pool['account.move']
        invoice_pool = self.pool['account.invoice']
        distinta_lines = self.pool['riba.distinta.line'].browse(
            cr, uid, active_ids, context=context)
        wizard = self.browse(cr, uid, ids)[0]
        if (not wizard.unsolved_journal_id or
                not wizard.bank_account_id or
                not wizard.bank_expense_account_id):
            raise UserError(_('Every account is mandatory'))
        line_id = []
        unsolved_desc = ''
        unsolved_amount = 0
        for distinta_line in distinta_lines:
            for riba_move_line in distinta_line.move_line_ids:
                if riba_move_line.move_line_id.account_id.id == distinta_line.\
                        partner_id.property_account_receivable.id:
                    line_id.append(
                        (0, 0, {
                            'name': _('Overdue Effects'),
                            'account_id': distinta_line.partner_id.\
                            property_account_receivable.id,
                            'debit': riba_move_line.amount,
                            'credit': 0.0,
                            'partner_id': distinta_line.partner_id.id,
                            'date_maturity': wizard.new_due_date or False,
                            'payment_term_type': wizard.new_payment_term_type
                                                 or False,
                            }),)
                    unsolved_desc += ' %s' % distinta_line.sequence
                    unsolved_amount += riba_move_line.amount
        line_id.append(
            (0, 0, {
                'name': _('Bank'),
                'account_id': wizard.bank_account_id.id,
                'credit': unsolved_amount + wizard.expense_amount,
                'debit': 0.0,
            }),)
        line_id.append(
            (0, 0, {
                'name':  _('Expenses'),
                'account_id': wizard.bank_expense_account_id.id,
                'debit': wizard.expense_amount,
                'credit': 0.0,
            }),)
        move_vals = {
            'ref': _('Unsolved Ri.Ba. %s - line %s') % (
                distinta_lines[0].distinta_id.name, unsolved_desc),
            'journal_id': wizard.unsolved_journal_id.id,
            'line_id': line_id,
        }
        move_id = move_pool.create(cr, uid, move_vals, context=context)

        for move_line in move_pool.browse(
                cr, uid, move_id, context=context).line_id:
            for distinta_line in distinta_lines:
                if move_line.account_id.id == distinta_line.partner_id.\
                        property_account_receivable.id:
                    for riba_move_line in distinta_line.move_line_ids:
                        invoice_ids = []
                        if riba_move_line.move_line_id.invoice:
                            invoice_ids = [
                                riba_move_line.move_line_id.invoice.id]
                        elif riba_move_line.move_line_id.unsolved_invoice_ids:
                            invoice_ids = [
                                i.id for i in
                                riba_move_line.move_line_id.
                                unsolved_invoice_ids
                            ]
                        invoice_pool.write(cr, uid, invoice_ids, {
                            'unsolved_move_line_ids': [(4, move_line.id)],
                        }, context=context)

                distinta_line.write({
                    'unsolved_move_id': move_id,
                    'state': 'unsolved',
                })
                distinta_line.distinta_id.signal_workflow('unsolved')
        return {
            'name': _('Unsolved Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id or False,
        }