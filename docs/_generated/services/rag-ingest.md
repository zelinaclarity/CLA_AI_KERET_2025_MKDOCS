# rag-ingest

**Image:** `aiclarity.hu:8443/docker-ssl/rag-ingest:py312-lo`

## Depends on

- `litellm`
- `litellm-pgvector`

## Environment

- `VECTOR_API_BASE_URL` = `http://litellm-pgvector:8000`
- `VECTOR_STORE_NAME` = `general`
- `RAG_VECTOR_STORE_API_KEY_FILE` = `/run/secrets/rag_vector_store_api_key`
- `LITELLM_BASE_URL` = `http://litellm:4000`
- `LITELLM_PGVECTOR_EMBED_SERVICE_VIRTUAL_KEY_FILE` = `/run/secrets/litellm_pgvector_embed_service_virtual_key`
- `EMBEDDING_MODEL` = `${EMBEDDING_MODEL}`
- `EMBEDDING_DIMENSIONS` = `${EMBEDDING_DIMENSIONS}`
- `DEPARTMENT` = `general`
- `SOURCE_DIR` = `/rag_source/general`
- `CHUNKER` = `llama`
- `CHUNK_SIZE` = `500`
- `CHUNK_OVERLAP` = `80`
- `MAX_EMBED_CHARS` = `4000`
- `RAG_META_DB_HOST` = `rag-db`
- `RAG_META_DB_PORT` = `5432`
- `RAG_META_DB_NAME` = `rag`
- `RAG_META_DB_USER` = `rag`
- `RAG_META_DB_PASSWORD_FILE` = `/run/secrets/rag_db_password`

## Secrets

- `rag_vector_store_api_key` (./secrets/rag_vector_store_api_key)
- `litellm_pgvector_embed_service_virtual_key` (./secrets/litellm_pgvector_embed_service_virtual_key)
- `rag_db_password` (./secrets/rag_db_password)

## Volumes

- `./rag/rag_ingest:/app:rw`
- `./rag/rag_source:/rag_source:rw`
- `./rag/rag_profile:/rag_profile:r`
