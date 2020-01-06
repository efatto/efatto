# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'l10n_it_generic', 'migrations/12.0.0.0.1/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'l10n_it_generic.transfer_account_id',
        ],
    )
