# hit-events-worker

**Image:** `python:3.12-slim`

## Depends on

- `litellm-db`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `DB_HOST` = `litellm-db`
- `DB_PORT` = `5432`
- `DB_NAME` = `litellm`
- `DB_USER` = `litellm`
- `DB_PASSWORD_FILE` = `/run/secrets/litellm_db_password`
- `POLL_SECONDS` = `30`
- `BATCH_SIZE` = `200`
- `MAX_TRIGGER_MESSAGE_LEN` = `2000`
- `DEBUG_SQL` = `false`

## Secrets

- `litellm_db_password` (./secrets/litellm_db_password)

## Volumes

- `./litellm/hit_events_worker.py:/app/hit_events_worker.py:ro`
