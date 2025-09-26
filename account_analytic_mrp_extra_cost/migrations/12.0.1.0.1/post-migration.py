import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    lines = env["account.analytic.line"].search([])
    i_max = len(lines)
    i = 0
    for line in lines:
        i += 1
        line._compute_extra_cost()
        _logger.info("Recomputed analytic cost for analytic line #%s/%s" % (i, i_max))
