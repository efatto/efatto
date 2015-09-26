import erppeek
import logging

logging.basicConfig(filename='update_stock_move_price_unit.log', level=logging.DEBUG)

client = erppeek.Client('http://localhost:8069', db='', user='admin', password='')

stock_moves = client.StockMove.browse([])
i = 0
for move in stock_moves:
    if move.picking_id:
        if move.picking_id.purchase_id:
            if move.purchase_line_id:
                i += 1
                currency_obj = client.ResCurrency
                if move.purchase_line_id.discount:
                    raw_price = move.purchase_line_id.price_unit * (1 - move.purchase_line_id.discount / 100)
                else:
                    raw_price = move.purchase_line_id.price_unit
                new_price = currency_obj.compute(move.picking_id.purchase_id.currency_id.id, move.company_id.currency_id.id,
                                                 raw_price, round=False)
                if move.price_unit != new_price:
                    logging.info(('updated move_id %s art. %s from %f old value to %f new value') % (move.id, move.product_id.name, move.price_unit, new_price))
                    move.price_unit = new_price
                    if i == 20:
                        break
