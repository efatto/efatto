Questo modulo calcola il costo effettivo sostenuto da fatture o note di credito fornitori per prodotto in relazione al consumo dei componenti di una produzione.

Nel caso in cui in fattura ci siano prodotti non presenti nei movimenti di scarico della produzione oppure ci siano servizi, vanno imputati interamente attraverso il sistema di reportistica in uso.

Il modulo quindi estrae per ogni riga delle fatture/note di credito acquisti con il conto analitico della produzione e lo stesso prodotto, il costo d'acquisto unitario. La media pesata del costo d'aquisto delle righe analitiche con lo stesso prodotto verrà moltiplicata per la somma delle quantità consumate nelle produzioni collegate a quel conto analitico.

La quantità che prevale è quindi quella indicata nei consumi delle produzioni, ignorando quindi acquisti fatturati per quantità superiori.

Un possibile report potrebbe quindi esporre le seguenti informazioni:

#. materiali consumati da magazzino interno, per i quali non c'è stata una fattura di acquisto che abbia generato righe analitiche (es. senza rotta MTO o l'ordine generato non è stato fatturato, oppure materiali presi da magazzino generico)
#. materiali consumati da acquisti specifici per i prodotti presenti nelle produzioni collegate al conto analitico (solo per la quantità effettivamente utilizzata, esclusi le eventuale eccedenze che verranno stoccate a magazzino)
#. differenza costo effettivo rispetto a costi analitici: questo valore segnala possibili errori di scarico nelle produzioni collegate al conto analitico. Fa questa operazione: somma tutti i consumi per prodotto da movimenti di magazzino non annullati generati dalla produzione; da questi consumi calcola il saldo della quantità da scaricare per ogni riga analitica per data di acquisto, in modo da restituire la quantità residua per quella riga: se resta un valore di differenza per l'ultima riga, la mostra a video. Il valore dovrebbe essere 0, se non lo è vuol dire che: se positivo, i consumi da righe analitiche sono inferiori ai consumi da righe di magazzino. Viceversa se negativo.
#. tutti i movimenti da righe analitiche di cui non si trova un corrispondenza nella produzione (confrontati per prodotto) vengono qui rendicontati, indipendentemente dalle quantità indicate.

Costo montaggi e costo accessori: sono valutate sono per la presenza del riferimento al conto analitico, indipendentemente dall'utilizzo o meno sulla produzione.

Nella produzione eseguita non sono presenti servizi, quindi non sono rilevanti.
