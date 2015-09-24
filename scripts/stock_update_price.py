import erppeek
client = erppeek.Client('http://localhost:8079', db='afmac_fifo_280615', user='admin', password='83claudio')

stock_moves = client.StockMove.browse([])
for move in stock_moves:
    if move.picking_id:
        if move.picking_id.purchase_id:
            if move.purchase_line_id:
                if move.purchase_line_id.discount:
                    move_cost = move.purchase_line_id.price_unit * (1 - move.purchase_line_id.discount / 100)
                    if move.price_unit != move_cost:
                        move.price_unit = move_cost
