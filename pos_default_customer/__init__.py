# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models

import logging
from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    res_partner_model = registry['res.partner']
    account_chart_template_model = registry['account.chart.template']
    chart_id = account_chart_template_model.search(cr, SUPERUSER_ID, [
        ('name', 'ilike', 'Italy')])
    chart = account_chart_template_model.browse(cr, SUPERUSER_ID, chart_id)[0]
    account_model = registry['account.account']
    account_id = account_model.search(cr, SUPERUSER_ID, [
        ('code', '=', chart.property_account_receivable[0].code)])[0]
    logging.getLogger('openerp.addons.pos_default_customer').info(
        'Create default partner corrispettivi')
    partner_id = res_partner_model.create(cr, SUPERUSER_ID, {
        'name': 'Corrispettivi default',
        'customer': True,
        'property_account_receivable': account_id,
    })
    pos_config_model = registry['pos.config']
    pos_config_ids = pos_config_model.search(cr, SUPERUSER_ID, [])
    for pos_config_id in pos_config_ids:
        pos_config_model.write(cr, SUPERUSER_ID, pos_config_id, {
            'partner_id': partner_id})
