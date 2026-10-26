# terrasini-mappa-dati

File di dati aperti usati dalla Futura Mappa · Terrasini (https://trupianovisual.com/strumenti/mappa-terrasini).

- `carburanti.json`: distributori di Terrasini e dintorni (entro 10 km) con i prezzi comunicati al Ministero. Si riscrive ogni giorno.
  - Fonte: Ministero delle Imprese e del Made in Italy, Osservatorio prezzi carburanti, dataset «Carburanti, prezzi praticati e anagrafica degli impianti» (https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti).
  - Licenza dei dati: IODL 2.0 (https://www.dati.gov.it/iodl/2.0/). I prezzi li comunicano i gestori: vale il prezzo esposto alla pompa.
- `aggiorna_carburanti.py`: lo script che scarica i file del Ministero e scrive `carburanti.json` (solo libreria standard di Python).
