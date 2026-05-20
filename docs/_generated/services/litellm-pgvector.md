# litellm-pgvector

**Image:** `aiclarity.hu:8443/docker-ssl/litellm-pgvector:b553f84`

## Depends on

- `rag-db`
- `litellm`

## Ports

- `8001:8000`

## Environment

- `DATABASE_URL` = `postgresql://rag:${RAG_DB_PASSWORD}@rag-db:5432/rag?schema=public`
- `SERVER_API_KEY` = `${RAG_VECTOR_STORE_API_KEY}`
- `HOST` = `0.0.0.0`
- `PORT` = `8000`
- `EMBEDDING__BASE_URL` = `http://litellm:4000`
- `EMBEDDING__API_KEY` = `${LITELLM_PGVECTOR_EMBED_SERVICE_VIRTUAL_KEY}`
- `EMBEDDING__MODEL` = `${EMBEDDING_MODEL_PROVIDER}/${EMBEDDING_MODEL}`
- `EMBEDDING__DIMENSIONS` = `${EMBEDDING_DIMENSIONS}`

## Volumes

- `./litellm-pgvector/entrypoint.sh:/entrypoint.sh:ro`
