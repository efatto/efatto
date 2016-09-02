# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
        string='Priority', help='Higher priority put project higher on trees.',
        default='1')
