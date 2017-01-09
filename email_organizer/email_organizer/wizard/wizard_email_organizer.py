# -*- coding: utf-8 -*-
from openerp import models, fields, api


class WizardEMailOrganizer(models.TransientModel):
    _name = 'wizard.email.organizer'

    def _get_message(self, message_id):
        message_pool = self.env['mail.message']
        return message_pool.browse(message_id)

    def _select_models(self):
        module_pool = self.env['ir.model']
        message = self._get_message(self._default_message_id())
        modules = module_pool.search(
            ['|', ('email_organizer', '=', True),
             ('model', '=', message.model)],
            order="name")

        return [(m.model, m.name) for m in modules]

    def _default_message_id(self):
        return self.env.context.get('active_id', None)

    def _default_filter_by(self):
        message = self._get_message(self._default_message_id())
        if not message.model or not message.res_id:
            return 'author'
        return 'partner'

    message_id = fields.Many2one(
        'mail.message', string="Message", required=True,
        default=_default_message_id)
    res_id = fields.Integer("Resource")
    model = fields.Selection(_select_models, string='Model')
    subject = fields.Char('Subject', related="message_id.subject",
                          readonly=True)
    body = fields.Html('Body', related="message_id.body", readonly=True)
    email_from = fields.Char('Email', related="message_id.email_from",
                             readonly=True)
    author_id = fields.Many2one(
        'res.partner', string='Author', related="message_id.author_id",
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', readonly=True)
    filter_by = fields.Selection(
        [('author', 'Author'), ('partner', 'Partner')],
        string='Filter by', default=_default_filter_by)
    is_filter_visible = fields.Boolean('Is filter visible', default=False)

    @api.onchange('model', 'filter_by', 'author_id')
    def onchange_model(self):
        res = {}
        domain = {'res_id': []}
        message = None
        if self.message_id:
            message = self._get_message(self.message_id.id)
        if message and self.model != message.model:
            self.res_id = None
        if self.model:
            obj_pool = self.env[self.model]
            if 'partner_id' in obj_pool._columns:
                if self.filter_by == 'author':
                    domain = {
                        'res_id': [('partner_id', '=', self.author_id.id)]}
                elif self.filter_by == 'partner':
                    domain = {
                        'res_id': [('partner_id', '=', self.partner_id.id)]}

                self.is_filter_visible = True
            else:
                self.is_filter_visible = False
        else:
            self.is_filter_visible = False
            self.res_id = None
        res.update({'domain': domain})
        return res

    @api.onchange('message_id')
    def onchange_message_id(self):
            res = {}
            if not self.message_id:
                return res
            message = self._get_message(self.message_id.id)
            obj = None
            if message.model and message.res_id:
                obj_pool = self.env[message.model]
                obj = obj_pool.browse(message.res_id)
                self.res_id = obj.id
                if 'partner_id' in obj_pool._columns:
                    self.partner_id = obj.partner_id.id
            self.model = message.model

    @api.multi
    def confirm(self):
        for organizer in self:
            message_pool = organizer.env['mail.message'].sudo()
            message = message_pool.browse(organizer.message_id.id)
            data = {'model': organizer.model, 'res_id': organizer.res_id}
            message.write(data)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
