Nelle regole di riordino sono stati aggiunti dei campi:

un campo che visualizza le quantità attualmente in ordini di acquisto in
stato bozza od inviato:

![Acquisti in bozza](../static/description/rdp_acquisto.png)

e un campo disponibilità virtuale, che somma alla quantità virtuale
quella del campo precedente, mostrandola solo nel caso sia negativa:

![Disponibilità virtuale con acquisti in bozza](../static/description/totale_con_rdp_acquisto.png)

È stato aggiunto inoltre un campo ricercabile che permette di filtrare
le regole di riordino la cui quantità virtuale prevista è negativa (può
capitare nel caso in cui gli ordini di acquisto o le produzioni non
siano state ancora processate in quanto i tempi di riapprovvigionamento
sono inferiori al tempo mancante all'utilizzo delle merci):

![Manca quantità virtuale nell'ubicazione](../static/description/manca_qta_virtuale.png)

che è possibile vedere (a scelta) nella vista elenco:

![Quantità virtuale mancante nell'ubicazione](../static/description/qta_virtuale_mancante.png)
