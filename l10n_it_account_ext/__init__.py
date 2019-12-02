# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models

import logging
from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    account_journal_model = registry['account.journal']
    logging.getLogger('openerp.addons.l10n_it_account_ext').info(
        'Setting values for account.journal group_invoice_lines '
        'and update_posted')
    all_journal_ids = account_journal_model.search(cr, SUPERUSER_ID, [])
    account_journal_model.write(cr, SUPERUSER_ID, all_journal_ids, {
        'update_posted': True,
        })
    invoices_journal_ids = account_journal_model.search(cr, SUPERUSER_ID, [
        ('type', 'in', [
            'sale', 'sale_refund', 'purchase', 'purchase_refund', ]),
        ])
    account_journal_model.write(cr, SUPERUSER_ID, invoices_journal_ids, {
        'group_invoice_lines': True,
        })
    cash_bank_journal_ids = account_journal_model.search(cr, SUPERUSER_ID, [
        ('type', 'in', ['cash', 'bank', 'general', ]),
        ])
    account_journal_model.write(cr, SUPERUSER_ID, cash_bank_journal_ids, {
        'entry_posted': True,
        })

    account_fiscalposition_model = registry['account.fiscal.position']
    logging.getLogger('openerp.addons.l10n_it_account_ext').info(
        'Setting values for account.fiscal.position standard journals')
    fiscal_position_id = account_fiscalposition_model.search(
        cr, SUPERUSER_ID, [('name', '=', 'Italia')], limit=1)
    sale_journal_id = account_journal_model.search(cr, SUPERUSER_ID, [
        ('type', 'in', ['sale', ]), ('code', '=', 'SAJ')], limit=1)
    if not sale_journal_id:
        sale_journal_id = account_journal_model.search(cr, SUPERUSER_ID, [
            ('type', 'in', ['sale', ]), ('code', 'ilike', 'VEN')], limit=1)
    if not sale_journal_id:
        sale_journal_id = account_journal_model.search(cr, SUPERUSER_ID, [
            ('type', 'in', ['sale', ])], limit=1)
    purchase_journal_id = account_journal_model.search(cr, SUPERUSER_ID, [
        ('type', 'in', ['purchase', ]), ('code', '=', 'EXJ')], limit=1)
    if not purchase_journal_id:
        purchase_journal_id = account_journal_model.search(cr, SUPERUSER_ID, [
            ('type', 'in', ['purchase', ]), ('code', 'ilike', 'ACQ')], limit=1)
    if not purchase_journal_id:
        purchase_journal_id = account_journal_model.search(cr, SUPERUSER_ID, [
            ('type', 'in', ['purchase', ])], limit=1)
    account_fiscalposition_model.write(cr, SUPERUSER_ID, fiscal_position_id, {
        'sale_journal_id': sale_journal_id[0],
        'purchase_journal_id': purchase_journal_id[0],
    })