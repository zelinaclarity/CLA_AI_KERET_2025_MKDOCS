# Hit Events Worker

## Cél

A `hit-events-worker` egy háttérfolyamat, amely a LiteLLM adatbázisából dolgozik.

## Compose szerep

- image: `python:3.12-slim`
- container_name: `hit-events-worker`
- restart: `unless-stopped`

## Függőségek

- `litellm-db`

## Mountok

- `./litellm/hit_events_worker.py:/app/hit_events_worker.py:ro`
- `vault-secrets:/secrets:ro`

## Fő konfiguráció

- DB host / port / name / user
- password file
- poll időköz
- batch méret
- SQL debug flag

## Indítás

A service induláskor telepíti a `psycopg2-binary` csomagot, majd futtatja a `hit_events_worker.py` scriptet.

## Fejlesztői megjegyzések

- A kapcsolódó forrásfájl:
  - `litellm/hit_events_worker.py`
