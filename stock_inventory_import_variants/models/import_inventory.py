# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO


class ImportInventory(models.TransientModel):
    _inherit = 'import.inventory'

    @api.multi
    def action_import(self):
        self.ensure_one()
        """Load Inventory data from the CSV file."""
        ctx = self._context
        stloc_obj = self.env['stock.location']
        inventory_obj = self.env['stock.inventory']
        inv_imporline_obj = self.env['stock.inventory.import.line']
        product_obj = self.env['product.product']
        attribute_value_obj = self.env['product.attribute.value']
        if 'active_id' in ctx:
            inventory = inventory_obj.browse(ctx['active_id'])
        if not self.data:
            raise exceptions.Warning(_("You need to select a file!"))
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        location = self.location
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]
        # check if keys exist
        if not isinstance(keys, list) or 'code' not in keys:
            raise exceptions.Warning(
                _("Not 'code' keys found"))
        del reader_info[0]
        values = {}
        actual_date = fields.Date.today()
        inv_name = self.name + ' - ' + actual_date
        inventory.write({'name': inv_name,
                         'date': fields.Datetime.now(),
                         'imported': True, 'state': 'confirm'})
        variant_list = [
            '09',
            '18', '19',
            '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
            '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
        ]
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))
            prod_location = location.id
            if 'location' in values and values['location']:
                locations = stloc_obj.search([('name', '=',
                                               values['location'])])
                prod_location = locations[:1].id
            if 'lot' in values and values['lot']:
                val['lot'] = values['lot']
            val['location_id'] = prod_location
            val['inventory_id'] = inventory.id
            val['fail'] = True
            val['fail_reason'] = _('No processed')
            prod_tmpl_lst = self.env['product.template'].search(
                [('prefix_code', '=', values['code'])])
            if prod_tmpl_lst:
                prod_tmpl_id = prod_tmpl_lst[0].id
                for var in variant_list:
                    if var in keys:
                        prefix = 'RB'
                        if values['material'] == '10':
                            prefix = 'T'
                        if values['material'] == '20':
                            prefix = 'M'
                        val['quantity'] = values[var]
                        val['code'] = values['code'] + \
                            values['material'] + prefix + var
                        if values[var]:
                            prod_lst = product_obj.search(
                                [('default_code', '=', values['code'] +
                                  values['material'] + prefix + var)])
                            color_attribute_value_id = attribute_value_obj.\
                                search([('code', '=', prefix + var)])
                            if prod_lst:
                                val['product'] = prod_lst[0].id
                            else:
                                product = product_obj.create({
                                    'product_tmpl_id': prod_tmpl_id,
                                    'attribute_value_ids':
                                        [(6, 0, [
                                            color_attribute_value_id.id])]
                                })
                                val['product'] = product.id
                            inv_imporline_obj.create(val)
