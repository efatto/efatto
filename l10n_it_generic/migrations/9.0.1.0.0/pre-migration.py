from openupgradelib import openupgrade


def migrate(cr, version):
    cr.execute("delete from ir_ui_view where arch like '%invoice_type_id%';")
    cr.execute('delete from ir_ui_view where id = 1260;')
