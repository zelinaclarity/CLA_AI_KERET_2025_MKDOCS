# RAG DB

## Cél

A `rag-db` a RAG rendszer pgvector alapú Postgres adatbázisa.

## Compose szerep

- image: `pgvector/pgvector:pg16`
- container_name: `rag-db`
- restart: `unless-stopped`

## Függőségek

- `vault-agent`

## Portok

- `5433:5432`

## Környezeti változók

- `POSTGRES_USER=rag`
- `POSTGRES_DB=rag`
- `POSTGRES_PASSWORD_FILE=/secrets/rag_db_password`

## Mountok

- `rag_db_data:/var/lib/postgresql/data`
- `vault-secrets:/secrets:ro`

## Kapcsolódó komponensek

- `litellm-pgvector`
- `rag-ingest`

## Fejlesztői megjegyzések

- Külön RAG architektúra fejezethez kapcsolódik.
- Érdemes dokumentálni:
  - vektor és meta adatok,
  - séma,
  - indexelési stratégia.
