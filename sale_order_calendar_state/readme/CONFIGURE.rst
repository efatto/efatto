Nell'ordine di vendita è stato aggiunto un campo calcolato che mostra lo stato della lavorazione dell'ordine in merito alla sua consegnabilità, denominato `Stato di calendario`:

.. image:: ../static/description/stato_di_calendario.png
    :alt: Stato di calendario

Nell'ordine di produzione è possibile selezionare uno stato aggiuntivo (in successivo sviluppo verrà calcolato in automatico):

.. image:: ../static/description/stato_aggiuntivo.png
    :alt: Stato aggiuntivo

Lo stato di calendario, visto che possono esserci diverse situazioni che si avverano allo stesso tempo (es. la produzione è avviata ma mancano dei componenti, prevale la mancanza di componenti) viene assegnato in base alla seguente priorità in ordine decrescente:

#. TOPROCESS
#. NOT_EVALUATED
#. PRODUCTION_NOT_EVALUATED
#. MISSING_COMPONENTS_BUY
#. MISSING_COMPONENTS_PRODUCE
#. PRODUCTION_PLANNED
#. SUBMANUFACTURE_STARTED
#. SUBMANUFACTURE_DONE
#. TEST_CHECK
#. PRODUCTION_READY
#. PRODUCTION_STARTED
#. PARTIALLYDELIVERED
#. AVAILABLEREADY
#. WAITING_FOR_PACKING
#. DELIVERY_READY
#. DONE_DELIVERY
#. INVOICED
#. SHIPPED
#. DONE
