Questo modulo aggiorna il prezzo dei movimenti di magazzino di scarico del prodotto (da vendita o produzione) con lo stesso conto analitico a partire da:

#. validazione fattura d'acquisto
#. validazione movimento di scarico

Il prezzo viene calcolato su una media ponderata sulle quantità fatturate, senza un controllo delle quantità (quindi qualsiasi quantità in acquisto viene utilizzata per calcolare il prezzo medio da imputare al prezzo unitario dei trasferimenti).

Es. acquisto 18 pz a 188€ ognuno e 10 pz a 265€ ognuno, per un totale di 28 pz e 6.034,00€, ad un prezzo medio di 215,50€.
Verrà quindi imputato un prezzo unitario di 215,50€ ai trasferimenti.

La funzione aggiorna inoltre tutti i movimenti di scarico/consumo successivi all'ingresso del materiale con o senza conto analitico per i quali non sia stato fatto l'aggiornamento con il prezzo medio sopra (es. un acquisto fatto precedentemente con un altro conto analitico o senza, in quanto una parte può essere rimasta a magazzino), con l'ultimo prezzo presente prima dello scarico (ad es. nel caso sopra uno scarico successivo al secondo acquisto, verrà valorizzato a 265€/cad, indifferentemente dalla quantità).
