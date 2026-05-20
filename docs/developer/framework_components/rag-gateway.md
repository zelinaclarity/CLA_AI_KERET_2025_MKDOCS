# RAG Gateway

## Cél

A `rag-gateway` a retrieval és kontextus-összeállító API réteg.

## Compose szerep

- image: `python:3.12-slim`
- container_name: `rag-gateway`
- restart: `unless-stopped`

## Függőségek

- `litellm`
- `litellm-pgvector`
- `litellm-db`

## Portok

- `8090:8080`

## Mountok

- `./rag-gateway:/app:ro`
- `vault-secrets:/run/secrets:ro`

## Fő konfiguráció

A compose alapján itt történik:
- vector store API használat
- RAG retrieval tuning
- LiteLLM kapcsolódás
- ops DB kapcsolódás

## Indítás

A konténer induláskor telepíti a requirements csomagokat, majd `uvicorn`-nal elindítja az `app:app` alkalmazást.

## Fejlesztői megjegyzések

- Külön figyelmet érdemel a runtime pip install, mert fejlesztési és üzemeltetési szempontból is fontos döntés.
