# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    # at installation default bookmark is when state is sent
    env["sale.order"].search([("state", "=", "sent")])._compute_bookmarked()
