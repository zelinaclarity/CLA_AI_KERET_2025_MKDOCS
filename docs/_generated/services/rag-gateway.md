# rag-gateway

**Image:** `python:3.12-slim`

## Depends on

- `litellm`
- `litellm-pgvector`
- `litellm-db`

## Ports

- `8090:8080`

## Environment

- `VECTOR_API_BASE_URL` = `http://litellm-pgvector:8000`
- `VECTOR_API_KEY_FILE` = `/run/secrets/rag_vector_store_api_key`
- `VECTOR_STORE_ID` = `${VECTOR_STORE_ID}`
- `TOP_K` = `5`
- `MIN_SCORE` = `0.50`
- `MAX_CONTEXT_CHARS` = `12000`
- `DYNAMIC_TOPK_FIRST` = `3`
- `DYNAMIC_TOPK_MAX` = `10`
- `RETURN_METADATA` = `true`
- `TASK_PREFIX` = `### Task:`
- `LITELLM_BASE_URL` = `http://litellm:4000`
- `LITELLM_API_KEY_FILE` = `/run/secrets/litellm_rag_gateway_virtual_key`
- `OPS_DB_HOST` = `litellm-db`
- `OPS_DB_PORT` = `5432`
- `OPS_DB_NAME` = `litellm`
- `OPS_DB_USER` = `litellm`
- `OPS_DB_PASSWORD_FILE` = `/run/secrets/litellm_db_password`

## Secrets

- `rag_vector_store_api_key` (./secrets/rag_vector_store_api_key)
- `litellm_rag_gateway_virtual_key` (./secrets/litellm_rag_gateway_virtual_key)
- `litellm_db_password` (./secrets/litellm_db_password)

## Volumes

- `./rag-gateway:/app:ro`
