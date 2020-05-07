from odoo import models, fields, api, _


class RibaList(models.Model):
    _inherit = 'riba.distinta'
    _order = 'date_created DESC'

    line_ids = fields.One2many(
        readonly=False,
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
        move_model = self.env['account.move']
        move_line_model = self.env['account.move.line']
        for line in self:
            journal = line.distinta_id.config_id.acceptance_journal_id
            total_credit = 0.0
            if not line.distinta_id.date_accepted:
                line.distinta_id.date_accepted = fields.Date.context_today(self)
            date_accepted = line.distinta_id.date_accepted
            move = move_model.create({
                'ref': 'C/O %s - Line %s' % (line.distinta_id.name, line.sequence),
                'journal_id': journal.id,
                'date': date_accepted,
            })
            to_be_reconciled = self.env['account.move.line']
            riba_move_line_name = ''
            for riba_move_line in line.move_line_ids:
                total_credit += riba_move_line.amount
                if riba_move_line.move_line_id.invoice_id.number:
                    riba_move_line_name += riba_move_line.move_line_id.invoice_id.number
                else:
                    if riba_move_line.move_line_id.name:
                        riba_move_line_name += riba_move_line.move_line_id.name
                move_line = move_line_model.with_context({
                    'check_move_validity': False
                }).create(
                    {
                        'name': (
                            riba_move_line.move_line_id.invoice_id and
                            riba_move_line.move_line_id.invoice_id.number or
                            riba_move_line.move_line_id.name),
                        'partner_id': line.partner_id.id,
                        'account_id': (
                            riba_move_line.move_line_id.account_id.id),
                        'credit': riba_move_line.amount if
                        riba_move_line.amount > 0 else 0.0,
                        'debit': 0.0 if riba_move_line.amount > 0 else
                        riba_move_line.amount * -1,
                        'move_id': move.id,
                        'date': date_accepted,
                    })
                to_be_reconciled |= move_line
                to_be_reconciled |= riba_move_line.move_line_id
            move_line_model.with_context({
                'check_move_validity': False
            }).create({
                'name': 'C/O %s-%s Rif. %s - %s' % (
                    line.distinta_id.name,
                    line.sequence,
                    riba_move_line_name,
                    line.partner_id.name),
                'account_id': (
                    line.acceptance_account_id.id or
                    line.distinta_id.config_id.acceptance_account_id.id
                    # in questo modo se la riga non ha conto accettazione
                    # viene prelevato il conto in configuration riba
                ),
                #  'partner_id': line.partner_id.id,  # tolto ancora dalla 8.0 perchè
                # è il conto di contropartita della banca, è utile rimetterlo?
                'date_maturity': line.due_date,
                'credit': 0.0,
                'debit': total_credit,
                'move_id': move.id,
                'date': date_accepted,
            })
            move.post()
            to_be_reconciled.reconcile()
            line.write({
                'acceptance_move_id': move.id,
                'state': 'confirmed',
            })
            line.distinta_id.state = 'accepted'
