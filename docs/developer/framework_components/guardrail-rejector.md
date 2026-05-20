# Guardrail Rejector

## Cél

A `guardrail-rejector` egy Python alapú FastAPI szolgáltatás a guardrail logika egyik elemeként.

## Compose szerep

- image: `python:3.12-slim`
- container_name: `guardrail-rejector`
- restart: `unless-stopped`

## Mountok

- `./litellm/rejector.py:/app/rejector.py:ro`

## Indítás

A konténer induláskor telepíti a `fastapi` és `uvicorn` csomagokat, majd elindítja a `rejector:app` alkalmazást a `8000` porton.

## Fejlesztői megjegyzések

- Külön dokumentálandó a guardrail láncban betöltött szerepe.
- A kapcsolódó fájl: `litellm/rejector.py`
