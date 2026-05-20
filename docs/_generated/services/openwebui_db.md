# openwebui_db

**Image:** `postgres:16-alpine`

## Ports

- `5434:5432`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `POSTGRES_USER` = `admin`
- `POSTGRES_DB` = `openwebui`
- `POSTGRES_PASSWORD_FILE` = `/run/secrets/openwebui_db_password`

## Secrets

- `openwebui_db_password` (./secrets/openwebui_db_password)

## Volumes

- `postgres_data:/var/lib/postgresql/data`
