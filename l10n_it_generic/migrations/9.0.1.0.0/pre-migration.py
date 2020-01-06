from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    cr.execute("delete from ir_ui_view where arch like '%invoice_type_id%';")
    cr.execute('delete from ir_ui_view where id = 1260;')

