# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.tools import float_round
from odoo.tools.date_utils import relativedelta

stock_options = {
    "from_stock": _("FROM STOCK"),
    "to_produce": _("TO PRODUCE"),
    "to_purchase": _("TO PURCHASE"),
}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_produce_delay(self, product_id, qty=0, bom_id=None):
        # get produce delay from bom operation multiplied by qty
        self.ensure_one()
        if not bom_id:
            found_bom_id = self.env["mrp.bom"]._bom_find(product=product_id)
            if found_bom_id:
                bom_id = found_bom_id
            else:
                bom_id = fields.first(product_id.bom_ids)
        if not qty:
            qty = self.product_uom_qty
        produce_delay = 0
        if bom_id.operation_ids:
            produce_delay = sum(
                [
                    float_round(
                        op.time_cycle_manual
                        * 100
                        / op.workcenter_id.time_efficiency
                        * qty,
                        precision_digits=0,
                        rounding_method="UP",
                    )
                    + op.workcenter_id.time_start
                    + op.workcenter_id.time_stop
                    for op in bom_id.operation_ids
                ]
            ) / (
                60 * 24  # 60 min * 24 hours = 1 day
            )
        elif product_id.produce_delay:
            produce_delay = product_id.produce_delay
        produce_delay = max(1, int(produce_delay))
        return bom_id, produce_delay

    def get_available_date(  # noqa: C901
        self,
        product_id,
        qty,
        date_start,
        available_date=False,
        level=0,
        commitment_date=False,
    ):
        child = "└"
        vertical = "─"
        available_info = []
        available_dates_info = ""
        stock_available_date = False
        (
            domain_quant_loc,
            domain_move_in_loc,
            domain_move_out_loc,
        ) = product_id._get_domain_locations()
        bom_id = False
        if hasattr(self, "bom_id") and self.bom_id:
            bom_id = self.bom_id
        bom_id, produce_delay = self._get_produce_delay(product_id, qty, bom_id)
        # FIXME: products with mto route in route_ids are never available from stock!
        incoming_stock_moves = self.env["stock.move"].search(
            [
                ("product_id", "=", product_id.id),
                ("product_uom_qty", ">", 0),
                ("state", "not in", ["done", "cancel"]),
                ("date", ">=", date_start),
            ]
            + domain_move_in_loc
        )
        reserved_stock_moves = self.env["stock.move"].search(
            [
                ("product_id", "=", product_id.id),
                ("product_uom_qty", ">", 0),
                ("state", "not in", ["done", "cancel"]),
                ("date", ">=", date_start),
            ]
            + domain_move_out_loc
        )
        # use stock move date as it is shown as scheduled date
        if reserved_stock_moves or incoming_stock_moves:
            for reserve_date in set(
                [x.date() for x in [w.date or w.date for w in reserved_stock_moves]]
                + [y.date() for y in [z.date or z.date for z in incoming_stock_moves]]
            ):
                available_info.append(
                    {
                        "info": "Stock move",
                        "date": reserve_date,
                        "qty": product_id.with_context(
                            to_date=reserve_date
                        ).virtual_available_at_date_move,
                    }
                )
        # FIXME when all dates have sufficient availability is ignored!
        # todo remove all availability with a previous availability with qty <
        #  requested qty, to prevent "steal" of goods from reserved moves
        #  get the available date later of the far available date with qty <
        if available_info:
            farther_unreservable_dates = [
                x["date"] for x in available_info if x["qty"] < qty
            ]
            if not farther_unreservable_dates:
                # all dates have sufficient qty
                farther_unreservable_dates = [min([x["date"] for x in available_info])]
                stock_available_date = farther_unreservable_dates[0]
            elif len(farther_unreservable_dates) == len(available_info):
                # None of the available dates meets the requested quantity
                stock_available_date = False
            else:
                stock_available_date = min(
                    [
                        x["date"]
                        for x in available_info
                        if x["date"] >= max(farther_unreservable_dates)
                        and x["qty"] >= qty
                    ]
                    or [False]
                )
        if bom_id:
            # if there is a specific bom selected, use it, else the first one
            # todo move to a overridable method to extend with other logics
            option = stock_options["to_produce"]
            avail_dates = []
            if stock_available_date:
                # available in stock
                available_date = stock_available_date
                option = stock_options["from_stock"]
                available_text = _(
                    "%s[BOM] [%s] [QTY: %s] [%s] plannable date %s.\n"
                ) % (
                    vertical * level,
                    product_id.default_code,
                    qty,
                    option,
                    available_date.strftime("%d/%m/%Y"),
                )
            else:
                for bom_line in bom_id.bom_line_ids.sorted(
                    key=lambda x: x.product_id.bom_ids, reverse=True
                ):
                    avail_date, avail_text = self.get_available_date(
                        bom_line.product_id,
                        qty * bom_line.product_qty,
                        date_start,
                        available_date,
                        level=level + 1,
                        commitment_date=commitment_date,
                    )
                    if avail_date:
                        avail_dates.append(avail_date)
                    if avail_text and avail_text not in available_dates_info:
                        available_dates_info += avail_text
                if avail_dates:
                    available_date = max(avail_dates)
                    available_text = _(
                        "%s[BOM] [%s] [QTY: %s] [%s] plannable date %s.\n"
                    ) % (
                        vertical * level,
                        product_id.default_code,
                        qty,
                        option,
                        available_date.strftime("%d/%m/%Y"),
                    )
                else:
                    available_text = _(
                        "%s[BOM] [%s] [QTY: %s] [%s] plannable date %s.\n"
                    ) % (
                        vertical * level,
                        product_id.default_code,
                        qty,
                        option,
                        "Not found",
                    )
            if available_date and not stock_available_date:
                # get current next available slot for this product in its workcenter
                if bom_id.operation_ids:
                    start_date = available_date
                    for operation in bom_id.operation_ids:
                        (
                            op_start_dt,
                            op_end_dt,
                        ) = operation.workcenter_id._get_first_available_slot(
                            # min(
                            fields.Datetime.to_datetime(start_date),
                            # (self.commitment_date or commitment_date)
                            # todo + relativedelta(-giorni di produzione totali? e come
                            #  aggiungere i tempi di lavorazione/ricezione dei figli?),
                            # ),
                            operation.time_cycle_manual * qty,
                        )
                        op_start_date = op_start_dt.date()
                        if op_start_date > start_date:
                            start_date = op_start_date
                    available_date = start_date
                    available_date += relativedelta(days=produce_delay)
                    available_text = _(
                        "%s[BOM] [%s] [QTY: %s] [%s] plannable start manufacturing "
                        "date %s, end manufacturing date %s.\n"
                    ) % (
                        vertical * level,
                        product_id.default_code,
                        qty,
                        option,
                        start_date.strftime("%d/%m/%Y"),
                        available_date.strftime("%d/%m/%Y"),
                    )
                elif produce_delay:
                    start_component_date = available_date
                    available_date += relativedelta(days=produce_delay)
                    available_text = _(
                        "%s[BOM] [%s] [QTY: %s] [%s] plannable start manufacturing "
                        "date %s, end manufacturing date %s.\n"
                    ) % (
                        vertical * level,
                        product_id.default_code,
                        qty,
                        option,
                        start_component_date.strftime("%d/%m/%Y"),
                        available_date.strftime("%d/%m/%Y"),
                    )
            if available_text and available_text not in available_dates_info:
                available_dates_info += available_text
        else:
            purchase_available_date = fields.Date.today() + relativedelta(
                days=int(product_id.purchase_delay)
            )
            if stock_available_date:
                # removed by customer request:
                # and stock_available_date <= purchase_available_date:
                # so get any future date of purchase order as available from stock
                available_date = stock_available_date
                option = stock_options["from_stock"]
                available_text = _(
                    "%s[COMP] [%s] [QTY: %s] [%s] plannable date %s.\n"
                ) % (
                    vertical * (level - 1) + child,
                    product_id.default_code,
                    qty,
                    option,
                    available_date.strftime("%d/%m/%Y"),
                )
            else:
                # Check if ordering the product the incoming date will be sooneer
                option = stock_options["to_purchase"]
                if not available_date or (
                    stock_available_date
                    and purchase_available_date < stock_available_date
                ):
                    available_date = purchase_available_date
                else:
                    # available in stock
                    available_date = stock_available_date
                    option = stock_options["from_stock"]
                available_text = _(
                    "%s[COMP] [%s] [QTY: %s] [%s] plannable date %s.\n"
                ) % (
                    vertical * (level - 1) + child,
                    product_id.default_code,
                    qty,
                    option,
                    available_date.strftime("%d/%m/%Y"),
                )

            if available_text not in available_dates_info:
                available_dates_info += available_text
        return available_date, available_dates_info
