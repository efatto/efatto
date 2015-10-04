import erppeek
import logging

logging.basicConfig(filename='update_stock_move_price_unit.log', level=logging.DEBUG)

client = erppeek.Client('http://localhost:8069', db='test', user='admin', password='admin')

stock_moves = client.StockMove.browse([])
i = 0
u = 0
logging.info('stock_moves len = %d' % len(stock_moves))
for move in stock_moves:
    if move.picking_id:
        if move.picking_id.purchase_id:
            if move.purchase_line_id:
                i += 1
                currency_obj = client.ResCurrency
                if move.purchase_line_id.discount:
                    raw_price = move.purchase_line_id.price_unit * (1 - move.purchase_line_id.discount / 100.0)
                else:
                    raw_price = move.purchase_line_id.price_unit
                new_price = currency_obj.compute(move.picking_id.purchase_id.currency_id.id, move.company_id.currency_id.id,
                                                 raw_price, round=False)
                if move.price_unit != new_price:
                    u += 1
                    logging.info(('#%d: updated move_id %s art. %s from %f old value to %f new value. Passed #%d moves with purchase id.') % (
                        u, move.id, move.product_id.default_code, move.price_unit, new_price, i))
                    move.price_unit = new_price
