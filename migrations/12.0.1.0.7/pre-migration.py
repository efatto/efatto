# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not version:
        return
    if not openupgrade.column_exists(cr, 'sale_order_line', 'predicted_arrival_late'):
        openupgrade.logged_query(
            env.cr,
            """
        ALTER TABLE sale_order_line
            ADD COLUMN IF NOT EXISTS predicted_arrival_late BOOLEAN
        """,
        )
        openupgrade.logged_query(
            env.cr,
            """
        UPDATE sale_order_line
            SET predicted_arrival_late = false
        """,
        )
    if not openupgrade.column_exists(cr, 'sale_order_line', 'available_date'):
        openupgrade.logged_query(
            env.cr,
            """
        ALTER TABLE sale_order_line
            ADD COLUMN IF NOT EXISTS available_date DATE
        """,
        )
        openupgrade.logged_query(
            env.cr,
            """
        UPDATE sale_order_line
            SET available_date = CURRENT_DATE 
        """,
        )
    if not openupgrade.column_exists(cr, 'sale_order_line', 'available_dates_info'):
        openupgrade.logged_query(
            env.cr,
            """
        ALTER TABLE sale_order_line
            ADD COLUMN IF NOT EXISTS available_dates_info VARCHAR
        """,
        )
        openupgrade.logged_query(
            env.cr,
            """
        UPDATE sale_order_line
            SET available_dates_info = '' 
        """,
        )
