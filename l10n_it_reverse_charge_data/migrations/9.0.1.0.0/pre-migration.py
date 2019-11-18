from openupgradelib import openupgrade


xmlid_renames = [
    ('l10n_it_invoice_intra_cee.auto_invoice_journal_sequence',
     'l10n_it_reverse_charge_data.auto_invoice_journal_sequence'),
    ('l10n_it_invoice_intra_cee.transfert_entry_journal_sequence',
     'l10n_it_reverse_charge_data.transfert_entry_journal_sequence'),
    ('l10n_it_invoice_intra_cee.auto_invoice_journal',
     'l10n_it_reverse_charge_data.auto_invoice_journal'),
    ('l10n_it_invoice_intra_cee.transfert_entry_invoice_journal',
     'l10n_it_reverse_charge_data.transfert_entry_invoice_journal'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlid_renames)
