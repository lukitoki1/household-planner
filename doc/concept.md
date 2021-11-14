# Aplikacja do zarządzania gospodarstwem domowym


## Funkcjonalność

Użytkownik rejestruje gospodarstwo domowe. Dodaje do niego innych użytkowników. W ramach gospodarstwa domowego tworzone są obowiązki z możliwością ustalenia kategorii, częstotliwości, przydzielenia użytkownika.  Możliwe jest tłumaczenie obowiązków (np. ktoś mieszka z obcokrajowcem) oraz powiadomienia o nadchodzącym obowiązku.
Analityk (można wyznaczyć taką rolę w IAM) może przygotowywać raporty o platformie dzięki eksportom do BigQuery.

## Technologia

- logowanie Google
- Frontend:
	- Buckety - React, serwowanie plików statycznych
- Backend:
	- App Engine - dowolnie: Go/Java/Python
	- Cloud Logging/Cloud Trace/Cloud Monitoring
	- Pub/Sub - powiadomienia
- Dane:
	- Spanner/Cloud SQL (Postgres)
	- Firestore - konfiguracja aplikacji
	- Secret Manager - przechowywanie sekretów
- DevOps:
	- Cloud Logging
	- Cloud Trace
	- Cloud Monitoring (wykresy)
	- Terraform
	- GitHub Actions
	- Uprawnienia IAM
- AI:
	- Tłumaczenie opisów obowiązków domowych
	- Text-to-speech

## Role

- Frontend - Łukasz K.
- Backend + Dane - Mateusz K.
- Backend + Dane - Rafał P.
- DevOps - Ernest Sz.
- Architektura + Backlog - Arkadiusz M.