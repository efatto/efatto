# __author__ = 'truongdung'
from openerp import fields, api, models
import json


class ShowFieldS(models.Model):
    _name = "show.fields"

    user_id = fields.Many2one(comodel_name="res.users", string="User Id")
    name = fields.Char(string="Name")
    model_name = fields.Char(string="Model Name")
    color = fields.Char(string="Color", default="check-base")
    fields_show = fields.Char(string="Fields Show")
    fix_header_list_view = fields.Boolean(string="Fix header List View")
    fields_sequence = fields.Char(string="Sequence")

    @api.model
    def action(self, vals, action):
        data = self.search([('user_id', '=', vals['user_id']), ('model_name', '=', vals['model_name'])])
        if action == 'update':
            if 'fields_show' in vals:
                vals['fields_show'] = str(vals['fields_show'])
                if len(data) > 0:
                    data[0].write({'fields_show': vals['fields_show'], 'fields_sequence': vals['fields_sequence']})
                else:
                    self.create(vals)
            else:
                if len(data) > 0:
                    data[0].write({'color': vals['color'], 'fix_header_list_view': vals['fix_header_list_view']})
                else:
                    self.create(vals)
        elif action == 'select':
            all_field_obj = self.env[vals['model_name']].fields_get()
            if len(data) > 0:
                data = data[0]
                return {'data': {'user_id': data.user_id.id, 'color': data.color, 'model_name': data.model_name,
                                 'fields_show': data.fields_show, 'id': data.id, 'name': data.name,
                                 'fields_sequence': data.fields_sequence,
                                 'fix_header_list_view': data.fix_header_list_view},
                        'fields': all_field_obj}
            else:
                return {'data': {}, 'fields': all_field_obj}

ShowFieldS()
