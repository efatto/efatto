# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class RibaList(models.Model):
    _inherit = 'riba.distinta'

    @api.one
    def _get_accreditation_move_ids(self):
        move_ids = self.env['account.move']
        for line in self.line_ids:
            move_ids |= line.accreditation_move_id
        self.accreditation_move_ids = move_ids

    @api.one
    def _get_accruement_move_ids(self):
        move_ids = self.env['account.move']
        for line in self.line_ids:
            move_ids |= line.accruement_move_id
        self.accruement_move_ids = move_ids

    @api.multi
    def riba_cancel(self):
        super(RibaList, self).riba_cancel()
        for riba_list in self:
            for line in riba_list.line_ids:
                if line.accreditation_move_id:
                    line.accreditation_move_id.unlink()

    @api.one
    def riba_accepted(self):
        super(RibaList, self).riba_accepted()
        self.date_accepted = self.date_accepted or \
            fields.Date.context_today(self)

    @api.one
    def riba_accredited(self):
        super(RibaList, self).riba_accredited()
        self.date_accreditation = self.date_accreditation or \
            fields.Date.context_today(self)

    accreditation_move_ids = fields.Many2many(
        'account.move',
        compute='_get_accreditation_move_ids',
        string="Accreditation Entries")
    accruement_move_ids = fields.Many2many(
        'account.move',
        compute='_get_accruement_move_ids',
        string="Accruement Entries")
    line_ids = fields.One2many(
        'riba.distinta.line', 'distinta_id', 'Riba deadlines', readonly=False,
        states={'paid': [('readonly', True)],
                'cancel': [('readonly', True)]})


class RibaListLine(models.Model):
    _inherit = 'riba.distinta.line'

    bank_riba_id = fields.Many2one(
        'res.bank', string='Debitor Bank for ri.ba.')
    accreditation_move_id = fields.Many2one(
        'account.move',
        string='Accreditation Entry',
        readonly=True)
    accruement_move_id = fields.Many2one(
        'account.move',
        string='Accruement Entry',
        readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('accredited', 'Accredited'),
        ('accrued', 'Accrued'),  # added state
        ('paid', 'Paid'),
        ('unsolved', 'Unsolved'),
        ('cancel', 'Canceled'),
    ], 'State', select=True, readonly=True, track_visibility='onchange')
    tobe_accredited = fields.Boolean(
        string='To be accredited')

    # total overwrite
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
            move_id = move_pool.create(self._cr, self.env.user.id, {
                'ref': 'Ri.Ba. %s - line %s' % (line.distinta_id.name,
                                                line.sequence),
                'journal_id': journal.id,
                'date': date_accepted,
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
                        'account_id': riba_move_line.move_line_id.account_id.id,
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
                #  'partner_id': line.partner_id.id,
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
