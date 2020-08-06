# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('account.account.history', 'res.partner.history'),
]

_table_renames = [
    ('account_account_history', 'res_partner_history'),
]


def _create_partner_history(cr):
    # create column partner_id in res_partner_history e fill with partner_id
    # linked with account_account
    openupgrade.logged_query(
        cr,
        """
    ALTER TABLE account_account_history
        ADD COLUMN IF NOT EXISTS partner_id INTEGER
    """,
    )
    # get first partner for property_account_receivable or property_account_payable
    openupgrade.logged_query(
        cr, """
        UPDATE account_account_history aah
        SET partner_id = (
            SELECT REPLACE(ip.res_id, 'res.partner,', '')::INTEGER FROM ir_property ip
            WHERE ip.name IN (
                'property_account_receivable_id', 'property_account_payable_id'
            )
            AND ip.value_reference = CONCAT('account.account,', aah.account_id)
            AND ip.res_id IS NOT NULL limit 1
        );
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(
        cr, 'account_account_history',
    ):
        _create_partner_history(cr)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
