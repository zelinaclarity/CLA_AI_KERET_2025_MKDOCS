# blocklist-cache-worker

**Image:** `python:3.12-slim`

## Depends on

- `litellm-db`
- `valkey`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `DB_HOST` = `litellm-db`
- `DB_PORT` = `5432`
- `DB_NAME` = `litellm`
- `DB_USER` = `litellm`
- `DB_PASSWORD_FILE` = `/run/secrets/litellm_db_password`
- `REDIS_URL` = `redis://valkey:6379/0`
- `SYNC_SECONDS` = `60`
- `BLOCKLIST_TABLE` = `custom_guardrails.blocklist`
- `REDIS_KEY_ACTIVE` = `cg:blocklist:active`

## Secrets

- `litellm_db_password` (./secrets/litellm_db_password)

## Volumes

- `./litellm/blocklist_cache_worker.py:/app/blocklist_cache_worker.py:ro`
