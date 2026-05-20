# Blocklist Cache Worker

## Cél

A `blocklist-cache-worker` a blocklist adatok adatbázisból Redis/Valkey cache-be szinkronizálását végzi.

## Compose szerep

- image: `python:3.12-slim`
- container_name: `blocklist-cache-worker`
- restart: `unless-stopped`

## Függőségek

- `litellm-db`
- `valkey`

## Mountok

- `./litellm/blocklist_cache_worker.py:/app/blocklist_cache_worker.py:ro`
- `vault-secrets:/secrets:ro`

## Fő konfiguráció

- DB kapcsolódás
- `REDIS_URL=redis://valkey:6379/0`
- `SYNC_SECONDS=60`
- `BLOCKLIST_TABLE=custom_guardrails.blocklist`
- `REDIS_KEY_ACTIVE=cg:blocklist:active`

## Indítás

A service induláskor telepíti a `psycopg2-binary` és `redis` csomagokat, majd futtatja a worker scriptet.

## Fejlesztői megjegyzések

- A guardrail / policy réteg részeként érdemes kezelni.
