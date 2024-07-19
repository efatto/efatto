Odoo mostra di default, sulla riga dell'ordine di vendita, un'icona di disponibilità del prodotto, in blu quando il sistema trova una disponibilità futura a stock del prodotto, in rosso in caso contrario.

.. image:: ../static/description/icona_azzurra.png
    :alt: Icona azzurra

.. image:: ../static/description/icona_rossa.png
    :alt: Icona rossa

Questo modulo nasconde questa icona quando l'ordine o la riga hanno una data di impegno, in quanto sarà compito di chi organizza gli approvvigionamenti fare in modo che questa data venga rispettata oppure di cambiarla, mentre chi ha completato la vendita non ha più competenza a riguardo.

Inoltre questo modulo modifica il comportamento dell'icona?
Quando l'icona è in blu mostra la quantità disponibile per coprire la richiesta alla prima data possibile, senza che questo prelievo incida sullo stock in modo da farlo diventare negativo.

Es. con una richiesta di 1 pz con un ordine alla data odierna del 01/07/2021 la disponibilità è immediata:

.. image:: ../static/description/richiesta_quantita.png
    :alt: Richiesta quantità iniziale

in quanto l'articolo è disponibile e lo stock previsto finale è superiore alla quantità richiesta. Con una richiesta di 4.662 pz la disponibilità è per il:

.. image:: ../static/description/richiesta_quantita_maggiore.png
    :alt: Richiesta quantità maggiore

in quanto l'articolo ha una quantità sufficiente a partire da quella data, e la quantità prevista finale è superiore a quella richiesta.

Quando l'icona è rossa segnala che non è possibile fornire da stock il prodotto:

.. image:: ../static/description/non_disponibile.png
    :alt: Non disponibile

Sull'ordine di vendita è stato aggiunto un bottone per calcolare la prima consegna possibile per tutte le righe dell'ordine:

.. image:: ../static/description/calcola.png
    :alt: Calcola

N.B.: la data di consegna include la somma dei tempi di produzione indicati nei prodotti ed eventuali semilavorati, per cui è 'cautelativa' (l'utente può prevedere una data di impegno inferiore alla data disponibile, in caso di necessità ed essendo a conoscenza della possibilità di farlo). Non prevede comunque calcoli sulla capacità dei centri di lavoro, per cui si considera infinita. La data di consegna inoltre considera il tempo di consegna degli acquisti dai fornitori. Invece il tempo di consegna al cliente non è considerato.

Nelle righe, in caso la data di impegno sia precedente la prima data disponibilità per la riga, è visibile un'icona di segnalazione:

.. image:: ../static/description/ritardo.png
    :alt: Ritardo

che apre un messaggio esplicativo dei dettagli dei componenti mancanti:

.. image:: ../static/description/messaggio.png
    :alt: Messaggio
