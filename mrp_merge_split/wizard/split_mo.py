# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, fields, models, _, exceptions

class Split_model(models.TransientModel):
    _name = 'split.model'
    _description = 'Spliting Model'
    
    name = fields.Many2one('mrp.production', 'Production')
    split_lot = fields.Integer(string='Qty', required=True)
    sp_id = fields.Many2one('split.mo', 'Split ref')
    
class Split_MO(models.TransientModel):
    _name = 'split.mo'
    _description = 'Spliting Manufacturing Order'
    
    split_lot = fields.Integer(string='Number of Lot:', required=True)
    data_mo_ids = fields.One2many('split.model', 'sp_id',
                                  string="Possible MO Lines")
    
    @api.onchange('split_lot')
    def onchange_split_lot(self):
        result = []
        if self.split_lot > 0:
            mrp_prod_obj = self.env['mrp.production']
            production = mrp_prod_obj.browse(self.env.context['active_id'])
            if self.split_lot > production.product_qty:
                raise exceptions.ValidationError(_(
                    "You could not allow to insert lot greater than MO Qty %s")
                    % production.product_qty
                )
            integer = int(production.product_qty)/self.split_lot
            remainder=int(production.product_qty)%self.split_lot
            for i in range(self.split_lot):
                result.append({'name':production.id,'split_lot':integer})
            if remainder>0 and len(result):
                result[-1]['split_lot'] += remainder
            self.data_mo_ids  = result

    @api.multi
    def split_mo(self):
        mo_obj = self.env['mrp.production']
        mo_id = mo_obj.browse(self.env.context['active_id'])
        total = 0.0
        for data in self.data_mo_ids:
            total += data.split_lot
        if total != mo_id.product_qty:
            raise exceptions.ValidationError(_(
                "You need to split the qty by includes found diff %s")
                                             % total-mo_id.product_qty)
        for data in self.data_mo_ids:
            res = mo_obj.product_id_change(mo_id.product_id.id, data.split_lot)
            copy_mo = mo_id.copy()
            copy_mo.write({'product_qty':data.split_lot, 'origin': mo_id.name})
        mo_id.write({'state':'cancel'})
        return True
