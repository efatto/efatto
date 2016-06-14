# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _, workflow
from openerp.exceptions import Warning as UserError


class RibaAccreditation(models.TransientModel):
    _inherit = "riba.accreditation"

    @api.multi
    def _get_accreditation_amount(self):
        super(RibaAccreditation, self)._get_accreditation_amount()
        amount = 0.0
        config = False
        if self._context.get('active_model', False) == 'riba.distinta.line':
            for line in self.env['riba.distinta.line'].browse(
                    self._context['active_ids']):
                if not config:
                    config = line.distinta_id.config_id
                if line.distinta_id.config_id != config:
                    raise UserError(
                        _('Error'),
                        _('Accredit only one bank configuration is possible'))
                if line.state in ['confirmed', ]:  # why was 'accredited' too?
                    amount += line.amount
        elif self._context.get('active_model', False) == 'riba.distinta':
            for line in self.env['riba.distinta'].browse(
                    self._context['active_id']).line_ids:
                if line.tobe_accredited and \
                        line.state in ['confirmed', ]:
                    # why was 'accredited' too?
                    amount += line.amount
        return amount

    @api.multi
    def _get_accreditation_date(self):
        res = False
        if self._context.get('active_model', False) == 'riba.distinta':
            res = self.env['riba.distinta'].browse(
                self._context['active_id']).date_accreditation
        return res

    @api.multi
    def create_move(self):
        self.ensure_one()
        ref = ''
        if self._context.get('active_model', False) == 'riba.distinta':
            active_id = self._context.get('active_id', False)
            if not active_id:
                raise UserError(_('Error'), _('No active ID found'))
            distinta = self.env['riba.distinta'].browse(active_id)
            if not self._context.get(
                    'accruement', False) and not \
                    distinta.config_id.accreditation_account_id:
                self.with_context(
                    accruement=True, accreditation_accruement=True)
            ref = distinta.name

        if self._context.get('active_model', False) == 'riba.distinta.line':
            active_ids = self._context.get('active_ids', False)
            if not active_ids:
                raise UserError(_('Error'), _('No active IDS found'))
            distinta_lines = self.env['riba.distinta.line'].browse(active_ids)
            last_id = ''
            for line in distinta_lines:
                if line.distinta_id.id != last_id:
                    ref += line.distinta_id.name + ' '
                last_id = line.distinta_id.id
            if not self._context.get(
                    'accruement', False) and not \
                    line.distinta_id.config_id.accreditation_account_id:
                self.with_context(
                    accruement=True, accreditation_accruement=True)

        if not (self.accreditation_journal_id or self.date_accreditation):
            raise UserError(
                _('Error'), _('Missing accreditation date or journal'))
        if not self._context.get('accruement', False):
            if not (self.bank_account_id or self.accreditation_account_id):
                raise UserError(_('Error'), _(
                    'Missing bank account or accreditation account'))
        if self._context.get('accruement', False):
            if not (self.acceptance_account_id and
                    self.accreditation_account_id):
                raise UserError(_('Error'), _(
                    'Missing acceptance or accredit account '
                    '(almost one is mandatory) '))
        date_accreditation = self.date_accreditation

        move_vals = {
            'ref': _('Accreditation Ri.Ba. %s') % ref,
            'journal_id': self.accreditation_journal_id.id,
            'date': date_accreditation,
            'line_id': [
                (0, 0, {
                    'name': _('Bank'),
                    'account_id': self._context.get(
                        'accruement', False) and not self._context.get(
                            'accreditation_accruement', False) and
                    self.accreditation_account_id.id or
                    self.bank_account_id.id,
                    'debit': self.bank_amount,
                    'credit': 0.0,
                    'date': date_accreditation,
                }),
                (0, 0, {
                    'name': _('Credit'),
                    'account_id': self._context.get('accruement', False) and
                    self.acceptance_account_id.id or
                    self.accreditation_account_id.id,
                    'credit': self.accreditation_amount,
                    'debit': 0.0,
                    'date': date_accreditation,
                }),
                #  removed bank expense row
            ]
        }

        move_id = self.env['account.move'].create(move_vals)
        accredited = True
        accrued = True
        if self._context.get('active_model', False) == 'riba.distinta':
            if self._context.get('accruement', False):
                for line in distinta.line_ids:
                    if line.tobe_accredited and not line.state == "accrued":
                        line.write({'accruement_move_id': move_id.id,
                                    'state': 'accrued'})
                    if not line.tobe_accredited:
                        accrued = False
                if accrued:
                    workflow.trg_validate(
                        self._uid, 'riba.distinta', active_id,
                        'accrued', self._cr)
            else:
                for line in distinta.line_ids:
                    if line.tobe_accredited and not line.state == "accredited":
                        line.write({'accreditation_move_id': move_id.id,
                                    'state': 'accredited'})
                    if not line.tobe_accredited:
                        accredited = False
                if accredited:
                    workflow.trg_validate(
                        self._uid, 'riba.distinta', active_id,
                        'accredited', self._cr)
        if self._context.get('active_model', False) == 'riba.distinta.line':
            if self._context.get('accruement', False):
                for line in distinta_lines:
                    if not line.state == "accrued":
                        line.write({'accruement_move_id': move_id.id,
                                    'state': 'accrued'})
            else:
                for line in distinta_lines:
                    if not line.state == "accredited":
                        line.write({'accreditation_move_id': move_id.id,
                                    'state': 'accredited'})
                        # TODO: if all lines of a distinta are accredited,
                        # set distinta accredited
        return {
            'name': _('Accreditation Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id.id or False,
        }

    acceptance_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Ri.Ba. acceptance account")
    date_accreditation = fields.Date(
        string='Accreditation date',
        default=_get_accreditation_date,
    )
    accreditation_amount = fields.Float(
        string='Credit amount',
        default=_get_accreditation_amount,
    )
    bank_amount = fields.Float(
        string='Versed amount',
        default=_get_accreditation_amount,
    )
