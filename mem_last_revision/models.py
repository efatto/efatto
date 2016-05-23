# -*- coding: utf-8 -*-

from openerp import models, fields, api


class mem_vehicle(models.Model):
    _inherit = 'mem.vehicle'

    oil_change_odometer = fields.Float("Last oil change (odometer)")
