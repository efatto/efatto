# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018-BroadTech IT Solutions
#    (<http://www.broadtech-innovations.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
##############################################################################

import uuid

from openerp import api, fields, models


class FatturaPAAttachment(models.Model):
    _inherit = "fatturapa.attachment.out"

    access_token = fields.Char('Token', readonly=True)

    @api.model
    def create(self, vals):
        res = super(FatturaPAAttachment, self).create(vals)
        res.access_token = uuid.uuid4()
        return res


class FatturaPAAttachmentIn(models.Model):
    _inherit = "fatturapa.attachment.in"

    access_token = fields.Char('Token', readonly=True)

    @api.model
    def create(self, vals):
        res = super(FatturaPAAttachmentIn, self).create(vals)
        res.access_token = uuid.uuid4()
        return res
