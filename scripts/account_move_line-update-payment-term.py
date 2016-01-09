import erppeek
import logging

logging.basicConfig(filename='update_account_move_line-payment-term.log', level=logging.DEBUG)

client = erppeek.Client('http://localhost:8079', db='afmac_110815', user='admin', password='83claudio')

account_move_line = client.AccountMoveLine.browse([])
i = 0
logging.info('account_move_line len = %d' % len(account_move_line))
for move in account_move_line:
    if move.invoice:
        if move.invoice.payment_term and move.invoice.payment_term.type:
            i += 1
            move.payment_term_type = move.invoice.payment_term.type
            logging.info(('#%d: updated move_id %s with invoice payment term %s to %s type. Passed #%d moves.') % (
                len(account_move_line), move.id, move.invoice.payment_term.name, move.invoice.payment_term.type, i))
