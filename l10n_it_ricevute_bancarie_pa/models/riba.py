# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class RibaListLine(models.Model):
    _inherit = 'riba.distinta.line'

    cig = fields.Char(
        compute='_get_cig_cup_values', string="CIG", size=256)
    cup = fields.Char(
        compute='_get_cig_cup_values', string="CUP", size=256)

    @api.one
    def _get_cig_cup_values(self):
        self.cig = ""
        self.cup = ""
        for move_line in self.move_line_ids:
            for related_document in move_line.move_line_id.invoice.\
                    related_documents:
                if related_document.cup:
                    self.cup = str(related_document.cup)
                if related_document.cig:
                    self.cig = str(related_document.cig)
