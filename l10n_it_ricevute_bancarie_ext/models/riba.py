# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class RibaList(models.Model):
    _inherit = 'riba.distinta'
    _order = 'date_created DESC'

    @api.multi
    def _get_accreditation_move_ids(self):
        self.ensure_one()
        move_ids = self.env['account.move']
        for line in self.line_ids:
            move_ids |= line.accreditation_move_id
        self.accreditation_move_ids = move_ids

    line_ids = fields.One2many(
        'riba.distinta.line', 'distinta_id', 'Riba deadlines', readonly=False,
        states={'paid': [('readonly', True)],
                'cancel': [('readonly', True)]})


class RibaListLine(models.Model):
    _inherit = 'riba.distinta.line'

    bank_riba_id = fields.Many2one(
        'res.bank', string='Debitor Bank for ri.ba.')

    # total overwrite to use date_accepted instead of registration_date for
    # accepted move, and other minor change in move line description
    @api.multi
    def confirm(self):
        move_pool = self.pool['account.move']
        move_line_pool = self.pool['account.move.line']
        for line in self:
            journal = line.distinta_id.config_id.acceptance_journal_id
            total_credit = 0.0
            if not line.distinta_id.date_accepted:
                raise UserError(_('Warning'), _('Missing Accepted Date'))
            date_accepted = line.distinta_id.date_accepted
            period_id = self.pool['account.period'].find(
                self._cr, self.env.user.id,
                line.distinta_id.registration_date)
            move_id = move_pool.create(self._cr, self.env.user.id, {
                'ref': 'Ri.Ba. %s - line %s' % (line.distinta_id.name,
                                                line.sequence),
                'journal_id': journal.id,
                'date': date_accepted,
                'period_id': period_id and period_id[0] or False,
            }, self._context)
            to_be_reconciled = []
            riba_move_line_name = ''
            for riba_move_line in line.move_line_ids:
                total_credit += riba_move_line.amount
                if riba_move_line.move_line_id.invoice.number:
                    riba_move_line_name += \
                        riba_move_line.move_line_id.invoice.number
                else:
                    if riba_move_line.move_line_id.name:
                        riba_move_line_name += riba_move_line.move_line_id.name
                move_line_id = move_line_pool.create(
                    self._cr, self.env.user.id, {
                        'name': riba_move_line_name,
                        'partner_id': line.partner_id.id,
                        'account_id':
                        riba_move_line.move_line_id.account_id.id,
                        'credit': riba_move_line.amount,
                        'debit': 0.0,
                        'move_id': move_id,
                        'date': date_accepted,
                    }, self._context)
                to_be_reconciled.append([move_line_id,
                                         riba_move_line.move_line_id.id])
            move_line_pool.create(self._cr, self.env.user.id, {
                'name': 'Ri.Ba. %s-%s Rif. %s - %s' % (line.distinta_id.name,
                                                       line.sequence,
                                                       riba_move_line_name,
                                                       line.partner_id.name),
                'account_id': (
                    line.acceptance_account_id.id or
                    line.distinta_id.config_id.acceptance_account_id.id
                    # in questo modo se la riga non ha conto accettazione
                    # viene prelevato il conto in configuration riba
                ),
                # 'partner_id': line.partner_id.id,
                'date_maturity': line.due_date,
                'credit': 0.0,
                'debit': total_credit,
                'move_id': move_id,
                'date': date_accepted,
            }, self._context)
            move_pool.post(
                self._cr, self.env.user.id, [move_id], self._context)
            for reconcile_ids in to_be_reconciled:
                move_line_pool.reconcile_partial(self._cr, self.env.user.id,
                                                 reconcile_ids,
                                                 self._context)
            line.write({
                'acceptance_move_id': move_id,
                'state': 'confirmed',
            })
            line.distinta_id.signal_workflow('accepted')
