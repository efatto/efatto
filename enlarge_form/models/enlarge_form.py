# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    enlarge_form = fields.Boolean(
        'Use full width of the screen?',
        help='Set to true if you want to widen view form so that it will'
             ' use full width of the screen.')

    @api.model
    def create(self, vals):
        result = super(IrUiView, self).create(vals)
        if result:
            self.manipulate_sheet_tag(result)
        return result

    @api.multi
    def write(self, vals):
        result = super(IrUiView, self).write(vals)
        if result:
            self.manipulate_sheet_tag(self)
        return result

    @api.multi
    def manipulate_sheet_tag(self, view):
        view.ensure_one()
        enlargement_view = str(view.model).replace('.', '_') + '_enlarge_form'

        # does a view already exist?
        view_ids = self.search(
            [('name', '=', enlargement_view), ('type', '=', 'form')])
        has_sheet_tag = view.arch.find('<sheet') >= 0 and True or False

        # what should we do?
        if view_ids:
            view_ids = view_ids[0]
            if not has_sheet_tag or not view.enlarge_form:
                #  deactivate_view
                view_ids.write({'active': False})
            else:
                # activate_view
                view_ids.write({'active': True})
        else:
            if has_sheet_tag and view.enlarge_form:
                # create_view
                view_arch = """<?xml version='1.0'?><xpath expr='//form/sheet' position='attributes'><attribute name='class'>enlarge_form</attribute></xpath>"""
                vals = {
                    'name': enlargement_view,
                    'type': 'form',
                    'model': view.model,
                    'inherit_id': view.id,
                    'arch': view_arch,
                    'xml_id': 'enlarge_form.' + enlargement_view,
                    'active': 'True',
                }
                res = self.create(vals)

                # for some reason, active was always getting saved as false
                if res:
                    self._cr.execute(
                        "UPDATE ir_ui_view SET active=TRUE WHERE id=%s" %
                        res.id)

        return True
