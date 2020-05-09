from odoo import models, fields, api


class RibaList(models.Model):
    _inherit = 'riba.distinta'

    @api.multi
    def _get_accreditation_move_ids(self):
        self.ensure_one()
        move_ids = self.env['account.move']
        for line in self.line_ids:
            move_ids |= line.accreditation_move_id
        self.accreditation_move_ids = move_ids

    @api.multi
    def _get_accruement_move_ids(self):
        self.ensure_one()
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

    @api.multi
    def riba_accepted(self):
        self.ensure_one()
        super(RibaList, self).riba_accepted()
        self.date_accepted = self.date_accepted or fields.Date.context_today(self)

    @api.multi
    def riba_accredited(self):
        self.ensure_one()
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
    state = fields.Selection(
        selection_add=[('accrued', 'Accrued')])


class RibaListLine(models.Model):
    _inherit = 'riba.distinta.line'

    accreditation_move_id = fields.Many2one(
        'account.move',
        string='Accreditation Entry',
        readonly=True)
    accruement_move_id = fields.Many2one(
        'account.move',
        string='Accruement Entry',
        readonly=True)
    state = fields.Selection(
        selection_add=[('accrued', 'Accrued')])
