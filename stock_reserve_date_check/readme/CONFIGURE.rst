Nell'ordine di vendita è stata aggiunta un'opzione, attivata di default ma che l'utente può disabilitare, che blocca la vendita con date di impegno non possibili:

.. image:: ../static/description/enable.png
    :alt: Abilita

Le date di impegno non possibili sono definite come:

#. l'acquisto del prodotto (o dei suoi componenti) per la data richiesta non è possibile, in quanto i tempi di consegna sono più lunghi
#. E la quantità disponibile nelle date degli scarichi di magazzino già prenotati sono inferiori dalla quantità richiesta O sono minori di zero O sono negativi

In caso il campo sia abilitato e l'impegno nella data richiesta non sia possibile esce un messaggio di errore:

.. image:: ../static/description/errore.png
    :alt: Errore

Che può essere risolto spostando la data di impegno, oppure disabilitando il controllo.

.. image:: ../static/description/disable.png
    :alt: Disabilita
