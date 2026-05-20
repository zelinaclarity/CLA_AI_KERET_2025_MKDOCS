# Presidio Anonymizer

## Cél

A `presidio-anonymizer` a Microsoft Presidio anonymizer service komponense.

## Compose szerep

- image: `mcr.microsoft.com/presidio-anonymizer:latest`
- container_name: `presidio-anonymizer`
- restart: `unless-stopped`

## Fejlesztői megjegyzések

- A compose alapján önálló szolgáltatásként fut.
- Érdemes később leírni, milyen adatvédelmi / anonimizálási folyamatban vesz részt.
