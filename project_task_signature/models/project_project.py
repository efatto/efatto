# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    worker_signature = fields.Binary(string="Worker's signature")
    recipient_signature = fields.Binary(string="Recipient's signature")
