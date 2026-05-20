# litellm

**Image:** `ghcr.io/berriai/litellm:v1.81.0-stable`

## Depends on

- `valkey`
- `litellm-db`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `LITELLM_CONFIG` = `/app/config.yaml`
- `STORE_MODEL_IN_DB` = `False`
- `PORT` = `4000`
- `REDIS_URL` = `redis://valkey:6379`
- `LITELLM_LOG` = `INFO`
- `OPENAI_API_KEY` = `sk-local`
- `USE_PRISMA_MIGRATE` = `false`
- `PHOENIX_COLLECTOR_HTTP_ENDPOINT` = `http://phoenix:6006/v1/traces`
- `PHOENIX_PROJECT_NAME` = `litellm`

## Secrets

- `litellm_db_password` (./secrets/litellm_db_password)
- `litellm_master_key` (./secrets/litellm_master_key)
- `litellm_salt_key` (./secrets/litellm_salt_key)

## Volumes

- `./litellm/config.yaml:/app/config.yaml:ro`
- `./litellm/custom_guardrail.py:/app/custom_guardrail.py:ro`
- `./litellm.secrets-entrypoint.sh:/entry/litellm.secrets-entrypoint.sh:ro`
