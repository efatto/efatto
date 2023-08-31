# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class Slide(models.Model):
    _inherit = "slide.slide"

    has_been_published = fields.Boolean(
        help="This flag is auto-checked when a slide is published, then it is "
        "unchanged even whether the slide is un-published, to block re-sending "
        "the same email many times for the sames slides."
    )

    def website_publish_button(self):
        # extend method from mixin website.published.mixin
        res = super().website_publish_button()
        if self.website_published:
            self.write({"has_been_published": True})
        return res

    def _post_publication(self):
        new_self = self.filtered(lambda x: not x.has_been_published)
        return super(Slide, new_self)._post_publication()
