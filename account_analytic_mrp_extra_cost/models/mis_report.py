from odoo import models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def drilldown(self, arg):
        # This code is very weird: it put the analytic account in the third item of the
        # domain, to use it in the search() (where the context is reset)
        self.ensure_one()
        domain = arg.get("domain", False)
        analytic_account_id = False
        for domain_item in domain:
            if any(x in domain_item[0] for x in ["account_id", "analytic_account_id"]):
                analytic_account_id = domain_item[2]
        if analytic_account_id:
            for i, domain_item in enumerate(domain):
                if domain_item[0] in ["has_mrp_raw_moves", "has_mrp_analytic_lines"]:
                    domain[i] = (
                        (domain_item[0], domain_item[1], analytic_account_id)
                    )
        return super().drilldown(arg)
