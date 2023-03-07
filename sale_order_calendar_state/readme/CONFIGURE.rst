Nell'ordine di vendita è stato aggiunto un campo calcolato che mostra lo stato della lavorazione dell'ordine in merito alla sua consegnabilità, denominato `Stato di calendario`:

.. image:: ../static/description/stato_di_calendario.png
    :alt: Stato di calendario

Nell'ordine di produzione è possibile selezionare uno stato aggiuntivo (in successivo sviluppo verrà calcolato in automatico):

.. image:: ../static/description/stato_aggiuntivo.png
    :alt: Stato aggiuntivo

Lo stato di calendario, visto che possono esserci diverse situazioni che si avverano allo stesso tempo (es. la produzione è avviata ma mancano dei componenti, prevale la mancanza di componenti) viene assegnato in base alla seguente priorità in ordine decrescente:

#. BLOCKED
#. TOPROCESS
#. PRODUCTION_NOT_EVALUATED
#. TO_ASSEMBLY
#. TO_SUBMANUFACTURE
#. TO_TEST
#. MISSING_COMPONENTS_PRODUCE
#. PRODUCTION_PLANNED
#. PRODUCTION_READY
#. PRODUCTION_STARTED
#. DONE
#. NOT_EVALUATED
#. MISSING_COMPONENTS_BUY
#. PARTIALLYDELIVERED
#. AVAILABLEREADY
#. WAITING_FOR_PACKING
#. DELIVERY_READY
#. DONE_DELIVERY
#. INVOICED
#. SHIPPED
