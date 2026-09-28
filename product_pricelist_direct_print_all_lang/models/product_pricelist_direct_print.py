from odoo import models


class ProductPricelistXlsx(models.AbstractModel):
    _inherit = "report.product_pricelist_direct_print_xlsx.report"

    def _prepare_header_row(self, book):
        row = super()._prepare_header_row(book)
        if book.show_all_langs:
            for lang in self.env["res.lang"].search([]):
                row.append(self.env._(lang.name))
            # Override first header column with default code
            row[0].write(self.env._("Default Code"))
        if book.categ_ids:
            categ_ids = book.categ_ids
            if book.show_child_categ:
                categ_ids |= self.env["product.category"].search(
                    [
                        ("id", "child_of", categ_ids.ids),
                    ]
                )
            if any(x.show_stock_available for x in categ_ids):
                book.show_stock_available = True
                row.append(self.env._("Available till stock lasts"))
        return row

    def _prepare_data_row_with_formats(self, book, product, formats):
        row = super()._prepare_data_row_with_formats(book, product, formats)
        if book.show_all_langs:
            for lang in self.env["res.lang"].search([]):
                row.append(product.with_context(lang=lang.code).name, None)
            # Override first column with default code
            row[0].write(product.default_code or "", None)
        if book.show_stock_available:
            if product.categ_id.show_stock_available:
                row.append(product.qty_available, None)
            else:
                row.append(self.env._("Not applicable"), None)
        return row
