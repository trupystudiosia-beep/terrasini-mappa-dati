# HANDOFF — terrasini-mappa-dati

Ricostruito il 28/10/2026 dalla cronologia GitHub e dal repo `trupianovisual` (passaggio a un nuovo account Claude Code). Nessuna memoria delle chat precedenti: dove qualcosa è dedotto lo dico.

## Stato attuale

- Repo **pubblico** di soli dati, 3 file, 2 commit (26/10 primo file, 27/10 aggiornamento). Nessun branch oltre `main`, nessuna PR, nessun issue.
- `aggiorna_carburanti.py` (solo libreria standard) scarica i due CSV del MIMIT (`anagrafica_impianti_attivi.csv`, `prezzo_alle_8.csv`, separatore `|` dal 10/02/2026), tiene i distributori di Terrasini + quelli entro 10 km dal centro (38.1522, 13.0832) e scrive `carburanti.json` e `carburanti.geojson`.
- Nel repo è versionato solo `carburanti.json` (il `.geojson` viene generato ma non committato).
- **Chi lo usa:** la Futura Mappa · Terrasini su `trupianovisual.com/strumenti/mappa-terrasini`. In `trupianovisual`, `public/strumenti/mappa-terrasini/dati/servizi/muoversi/percorsi.json` punta a `https://raw.githubusercontent.com/trupystudiosia-beep/terrasini-mappa-dati/main/carburanti.json`. C'è anche la route `/api/mappa/carburanti` (dati dal vivo) che, se il MIMIT non risponde a Vercel, risponde `disponibile: false` e la sezione ripiega sul file statico.
- **Chi lo aggiorna:** NON GitHub Actions (non c'è `.github/workflows`). I commit sono dell'account `trupystudiosia-beep` alle 10:00 ora italiana → quasi certamente l'attività pianificata di Windows sul PC di Giuseppe (`aggiorna_carburanti_pc.ps1 -Modo dati`, in `trupianovisual/public/strumenti/mappa-terrasini/dati/servizi/muoversi/automazione_carburanti/pc/`). Se il PC è spento, il file non si aggiorna.

## Decisioni prese (dal codice e dai commenti)

- Dati in un repo separato e pubblico così l'aggiornamento quotidiano **non richiede un deploy del sito** (il progetto Vercel del sito non è collegato a Git).
- Fonte unica: open data MIMIT, licenza **IODL 2.0**; attribuzione sempre nel file (`fonte`, `licenza`, `attribuzione`, `link_fonte`) e la nota «vale il prezzo esposto alla pompa».
- Raggio 10 km, impianti del Comune di Terrasini sempre inclusi anche oltre il raggio.
- GitHub Actions previsto solo se il MIMIT risponde ai server di GitHub: esiste un workflow di prova (`carburanti-prova.yml`) e uno giornaliero (`carburanti-giornaliero.yml`, cron 07:45 e 08:45 UTC) **non installati**. A Vercel il MIMIT risponde con `UND_ERR_CONNECT_TIMEOUT` (annotato nei commenti).

## Regole da rispettare

- Niente dipendenze esterne nello script (solo libreria standard Python).
- Non cambiare la forma del JSON senza aggiornare la sezione Muoversi della mappa e la route `/api/mappa/carburanti` in `trupianovisual` (stessi campi).
- Mantenere sempre fonte, licenza IODL 2.0 e attribuzione nel file.
- Lo User-Agent identifica il progetto e la mail di contatto: non toglierlo.
- Il file si riscrive solo se cambia qualcosa (niente commit vuoti).

## Prossimi passi (priorità)

1. Decidere chi aggiorna il file: lanciare a mano il workflow di prova su GitHub; se il MIMIT risponde, installare qui `carburanti-giornaliero.yml` e togliere la dipendenza dal PC.
2. Decidere se committare anche `carburanti.geojson` (lo script lo produce, il README non lo cita).
3. Allineare lo script con la copia in `trupianovisual` (`dati/servizi/muoversi/aggiorna_carburanti.py` citato nel workflow) per non averne due versioni diverse.
4. Opzionale: avviso se il file non si aggiorna da più di 2 giorni (la mappa mostra comunque `estrazione_mimit`).

## Dubbi da chiarire (Giuseppe)

- L'aggiornamento gira davvero dall'attività pianificata del PC? Va bene che dipenda dal PC acceso?
- Hai già provato il workflow di prova su GitHub Actions? Con che esito?
- Il `.geojson` serve alla mappa o basta il `.json`?
