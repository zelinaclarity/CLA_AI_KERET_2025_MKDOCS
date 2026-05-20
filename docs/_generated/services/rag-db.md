# rag-db

**Image:** `pgvector/pgvector:pg16`

## Ports

- `5433:5432`

## Environment

- `POSTGRES_USER` = `rag`
- `POSTGRES_DB` = `rag`
- `POSTGRES_PASSWORD_FILE` = `/run/secrets/rag_db_password`

## Secrets

- `rag_db_password` (./secrets/rag_db_password)

## Volumes

- `rag_db_data:/var/lib/postgresql/data`
