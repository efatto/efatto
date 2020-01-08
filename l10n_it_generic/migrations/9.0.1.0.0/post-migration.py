from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.load_data(
        cr, 'l10n_it_generic', 'migrations/9.0.1.0.0/noupdate_changes.xml',
    )
