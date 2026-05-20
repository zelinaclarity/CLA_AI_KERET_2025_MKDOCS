# LiteLLM PGVector

## Cél

A `litellm-pgvector` a vector store API réteg a RAG adatbázis és a LiteLLM embedding szolgáltatás között.

## Compose szerep

- image: `aiclarity.hu:8443/docker-ssl/litellm-pgvector:b553f84`
- container_name: `litellm-pgvector`
- restart: `unless-stopped`

## Függőségek

- `rag-db`
- `litellm`

## Portok

- `8001:8000`

## Fő konfiguráció

- host: `0.0.0.0`
- port: `8000`
- embedding base URL: `http://litellm:4000`
- model és embedding dimensions env változókból

## Mountok

- `./litellm-pgvector/entrypoint.sh:/entrypoint.sh:ro`
- `vault-secrets:/secrets:ro`

## Fejlesztői megjegyzések

- Fontos integrációs komponens a RAG láncban.
- A `litellm-pgvector/entrypoint.sh` külön dokumentálandó.
