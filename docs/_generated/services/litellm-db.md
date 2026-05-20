# litellm-db

**Image:** `postgres:16-alpine`

## Ports

- `5432:5432`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `POSTGRES_USER` = `litellm`
- `POSTGRES_DB` = `litellm`
- `POSTGRES_PASSWORD_FILE` = `/run/secrets/litellm_db_password`

## Secrets

- `litellm_db_password` (./secrets/litellm_db_password)

## Volumes

- `litellm-db:/var/lib/postgresql/data`
