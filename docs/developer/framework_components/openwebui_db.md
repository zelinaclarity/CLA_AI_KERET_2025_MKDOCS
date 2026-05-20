# OpenWebUI DB

## Cél

Az `openwebui_db` a Postgres adatbázis az OpenWebUI backend számára.

## Compose szerep

- image: `postgres:16-alpine`
- container_name: `openwebui_db`
- restart: `unless-stopped`

## Függőségek

- `vault-agent`

## Portok

- `5434:5432`

## Környezeti változók

- `TZ`
- `POSTGRES_USER=admin`
- `POSTGRES_DB=openwebui`
- `POSTGRES_PASSWORD_FILE=/secrets/openwebui_db_password`

## Mountok

- `postgres_data:/var/lib/postgresql/data`
- `vault-secrets:/secrets:ro`

## Fejlesztői megjegyzések

- Az OpenWebUI DB password Vaultból érkezik.
- Később érdemes külön leírni:
  - séma kezelést,
  - backup/restore logikát,
  - migrációs stratégiát.
