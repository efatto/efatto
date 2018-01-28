# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _, workflow
from openerp.exceptions import Warning as UserError


class RibaAccreditation(models.TransientModel):
    _inherit = "riba.accreditation"

    @api.multi
    def _get_accreditation_journal_id(self):
        if self._context.get('active_model', False) == 'riba.distinta.line':
            res = self.env['riba.configuration'].\
                get_default_value_by_list_line('accreditation_journal_id')
        else:
            res = super(
                RibaAccreditation, self)._get_accreditation_journal_id()
        return res

    @api.multi
    def _get_accreditation_account_id(self):
        if self._context.get('active_model', False) == 'riba.distinta.line':
            res = (self.env['riba.configuration'].
                   get_default_value_by_list_line('accreditation_account_id'))
        else:
            res = super(
                RibaAccreditation, self)._get_accreditation_account_id()
        return res

    @api.multi
    def _get_acceptance_account_id(self):
        res = self.env['riba.configuration'].\
            get_default_value_by_list_line('acceptance_account_id')
        return res

    @api.multi
    def _get_bank_account_id(self):
        if self._context.get('active_model', False) == 'riba.distinta.line':
            res = self.env['riba.configuration'].\
                get_default_value_by_list_line('bank_account_id')
        else:
            res = super(RibaAccreditation, self)._get_bank_account_id()
        return res

    @api.multi
    def _get_bank_expense_account_id(self):
        if self._context.get('active_model', False) == 'riba.distinta.line':
            res = self.env['riba.configuration'].\
                get_default_value_by_list_line('bank_expense_account_id')
        else:
            res = super(RibaAccreditation, self)._get_bank_expense_account_id()
        return res

    @api.multi
    def _get_accreditation_amount(self):
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
                if line.state == 'confirmed':
                    amount += line.amount
        elif self._context.get('active_model', False) == 'riba.distinta':
            amount = super(RibaAccreditation, self)._get_accreditation_amount()
        return amount

    @api.multi
    def _get_accruement_amount(self):
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
                        _('Accrue only one bank configuration is possible'))
                if line.state == 'accredited':
                    amount += line.amount
        return amount

    @api.multi
    def skip(self):
        if self._context.get('active_model', False) == 'riba.distinta.line':
            active_ids = self._context.get('active_ids', False)
            if not active_ids:
                raise UserError(_('Error'), _('No active IDS found'))
            distinta_lines = self.env['riba.distinta.line'].browse(active_ids)
            for line in distinta_lines:
                if not line.state == "accredited":
                    line.write({'state': 'accredited'})
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(RibaAccreditation, self).skip()

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
        context = {}
        # accredit only from distinta line
        active_ids = self._context.get('active_ids', False)
        if not active_ids:
            raise UserError(_('Error'), _('No active IDS found'))
        distinta_lines = self.env['riba.distinta.line'].browse(active_ids)
        distinta_id = distinta_lines[0].distinta_id
        ref = distinta_id.name

        if not (self.accreditation_journal_id or self.date_accreditation):
            raise UserError(
                _('Error'), _('Missing accreditation date or journal'))
        date_accreditation = self.date_accreditation

        move_vals = {
            'ref': _('Accreditation Ri.Ba. %s') % ref,
            'journal_id': self.accreditation_journal_id.id,
            'date': date_accreditation,
            'line_id': [
                (0, 0, {
                    'name': _('Bank'),
                    'account_id': self.bank_account_id.id,
                    'debit': self.bank_amount,
                    'credit': 0.0,
                    'date': date_accreditation,
                }),
                (0, 0, {
                    'name': _('Credit'),
                    'account_id': self.accreditation_account_id.id,
                    'credit': self.accreditation_amount,
                    'debit': 0.0,
                    'date': date_accreditation,
                }),
            ]
        }
        move_id = self.env['account.move'].create(move_vals)
        for line in distinta_lines:
            if not line.state == "accredited":
                line.write({'accreditation_move_id': move_id.id,
                            'state': 'accredited'})
        distinta_line_states = set(distinta_id.line_ids.mapped('state'))
        state_distinta = list(distinta_line_states)
        if len(state_distinta) == 1 and state_distinta[0] == 'accredited':
            workflow.trg_validate(
                self._uid, 'riba.distinta', distinta_id.id, 'accredited',
                self._cr)
        return {
            'name': _('Accreditation Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id.id or False,
        }

    @api.multi
    def create_accrue_move(self):
        self.ensure_one()
        ref = ''
        # accrue only from distinta lines
        active_ids = self._context.get('active_ids', False)
        if not active_ids:
            raise UserError(_('Error'), _('No active IDS found'))
        distinta_lines = self.env['riba.distinta.line'].browse(active_ids)
        distinta_id = ''
        for line in distinta_lines:
            if line.distinta_id != distinta_id:
                ref += line.distinta_id.name + ' '
            distinta_id = line.distinta_id

        if not (self.accreditation_journal_id or self.date_accreditation):
            raise UserError(
                _('Error'), _('Missing accreditation date or journal'))
        if not (self.bank_account_id or self.accreditation_account_id):
            raise UserError(_('Error'), _(
                'Missing bank account or accreditation account'))
        date_accruement = self.date_accruement

        move_vals = {
            'ref': _('Accruement Ri.Ba. %s') % ref,
            'journal_id': self.accreditation_journal_id.id,
            'date': date_accruement,
            'line_id': [
                (0, 0, {
                    'name': _('Bank'),
                    'account_id': self.accreditation_account_id.id,
                    'debit': self.accruement_amount,
                    'credit': 0.0,
                    'date': date_accruement,
                }),
                (0, 0, {
                    'name': _('Credit'),
                    'account_id': self.acceptance_account_id.id ,
                    'credit': self.accruement_amount,
                    'debit': 0.0,
                    'date': date_accruement,
                }),
            ]
        }

        move_id = self.env['account.move'].create(move_vals)
        for line in distinta_lines:
            if not line.state == "accrued":
                line.write({'accruement_move_id': move_id.id,
                            'state': 'accrued'})
        # todo if all lines of distinta are accrued, set distinta accrued
        state_distinta = list(set(distinta_id.line_ids.mapped('state')))
        if len(state_distinta) == 1 and state_distinta[0] == 'accrued':
            distinta_id.state = 'accrued'
            # workflow.trg_validate(
            #     self._uid, 'riba.distinta', distinta_id.id,
            #     'accrued', self._cr)

        return {
            'name': _('Movimento di maturazione ri.ba.'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id.id or False,
        }

    acceptance_account_id = fields.Many2one(
        comodel_name='account.account',
        default=_get_acceptance_account_id,
        string="Ri.Ba. acceptance account")
    date_accreditation = fields.Date(
        string='Accreditation date',
        default=lambda self: self._get_accreditation_date(),
    )
    date_accruement = fields.Date(
        string='Accruement date',
        default=lambda self: self._get_accreditation_date(),
    )
    accreditation_amount = fields.Float(
        string='Credit amount',
        default=lambda self: self._get_accreditation_amount(),
    )
    accruement_amount = fields.Float(
        string='Accrue amount',
        default=lambda self: self._get_accruement_amount(),
    )
    bank_amount = fields.Float(
        string='Versed amount',
        default=lambda self: self._get_accreditation_amount(),
    )
    bank_expense_account_id = fields.Many2one(
        comodel_name='account.account',
        default=lambda self: self._get_bank_expense_account_id(),
        string="Bank Expenses account")
    accreditation_journal_id = fields.Many2one(
        comodel_name='account.journal',
        default=lambda self: self._get_accreditation_journal_id(),
        string="Accreditation journal",
        domain=[('type', '=', 'bank')])
    accreditation_account_id = fields.Many2one(
        comodel_name='account.account',
        default=lambda self: self._get_accreditation_account_id(),
        string="Ri.Ba. bank account")
    bank_account_id = fields.Many2one(
        comodel_name='account.account',
        default=lambda self: self._get_bank_account_id(),
        string="Bank account",
        domain=[('type', '=', 'liquidity')])
