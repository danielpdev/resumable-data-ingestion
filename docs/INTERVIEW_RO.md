# Pregătire pentru interviu — Resumable Data Ingestion

Roluri țintă: Data Engineer / Python Backend.

## Prezentare de 90 de secunde

1. Explică problema concretă și cine folosește rezultatul.
2. Rulează `make demo` sau fluxul din UI.
3. Arată testul pentru un caz de eșec, apoi explică mecanismul din cod.
4. Spune ce limite are demonstrația și ce ai construi pentru producție.

Decizia de explicat: A batch ID hashes the immutable source content. Each row effect, validation failure and cursor update commit together. Bad rows enter quarantine; corrected input is a new batch and upserts the same business ID.

## Cinci întrebări

1. De ce hash pe input?
2. Ce se întâmplă dacă fișierul se schimbă?
3. Cum păstrezi cursorul consistent?
4. Cum reprocezi quarantine?
5. Ce înseamnă deduplicare pe business key?

## Exercițiu înainte de a aplica

Add streaming input, source provenance, distributed leases and explicit conflict policy.

Alege o parte mică a acestei modificări, implementeaz-o personal, adaugă un test care verifică comportamentul și descrie rezultatul într-un commit real. Nu declara că ai înțeles sau construit singur o parte pe care nu o poți explica.

## Checklist personal

- [ ] Pot porni proiectul dintr-un checkout curat.
- [ ] Pot urmări cererea până la rezultatul salvat.
- [ ] Pot explica diferența dintre fixture și model local.
- [ ] Pot demonstra un eșec și recuperarea lui.
- [ ] Am făcut o modificare proprie și o pot explica în engleză.

Aceste puncte necesită review-ul tău; nu au fost bifate automat.
