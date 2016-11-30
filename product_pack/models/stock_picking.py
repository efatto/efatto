#
#
#
# #uguali per stock.picking stock.picking.out sale.order
#     # Gestione Volume
#     # Colume nel package
#     if line.product_id.container_id:
#         if line.product_id.container_id.volume > 0:
#             volume = (converted_qty_package * line.product_id.container_id.volume)
#     else:
#         # Prodotto senza container
#         if line.product_id.volume > 0:
#             volume = (converted_qty * line.product_id.volume)
#         elif line.product_id.product_tmpl_id:
#             # Volume nel template
#             if line.product_id.product_tmpl_id.volume > 0:
#                 volume = (converted_qty * line.product_id.product_tmpl_id.volume )
#             # Volume nel package del template
#             elif line.product_id.product_tmpl_id.container_id:
#                 if line.product_id.product_tmpl_id.container_id.volume > 0:
#                     volume = \
#                     (converted_qty_package * line.product_id.product_tmpl_id.container_id.volume)
#
#     # Gestione del peso dei container
#     if line.product_id.container_id:
#         if line.product_id.container_id.weight_net > 0:
#             weight += (
#             converted_qty_package * line.product_id.container_id.weight_net)
#     elif line.product_id.product_tmpl_id:
#         if line.product_id.product_tmpl_id.container_id:
#             if line.product_id.product_tmpl_id.container_id.weight_net > 0:
#                 weight += (
#                 converted_qty_package * line.product_id.product_tmpl_id.container_id.weight_net)