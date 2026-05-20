# Presidio Analyzer

## Cél

A `presidio-analyzer` a Microsoft Presidio analyzer service komponense.

## Compose szerep

- image: `mcr.microsoft.com/presidio-analyzer:latest`
- container_name: `presidio-analyzer`
- restart: `unless-stopped`

## Fejlesztői megjegyzések

- A compose alapján önállóan fut a hálózaton.
- Később érdemes rögzíteni:
  - mely komponens használja,
  - milyen endpointokon érhető el belsőleg,
  - milyen PII / adatvédelmi use case-ekhez kapcsolódik.
