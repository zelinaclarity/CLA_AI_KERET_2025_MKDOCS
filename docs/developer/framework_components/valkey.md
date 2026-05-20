# Valkey

## Cél

A `valkey` a framework Redis-kompatibilis cache / state backendje.

## Compose szerep

- image: `valkey/valkey:7-alpine`
- container_name: `valkey`
- restart: `unless-stopped`

## Portok

- `6379:6379`

## Mountok

- `valkey_data:/data`

## Kapcsolódó komponensek

A compose alapján közvetlenül kapcsolódik hozzá:
- `litellm` (`REDIS_URL=redis://valkey:6379`)
- `blocklist-cache-worker` (`redis://valkey:6379/0`)

## Fejlesztői megjegyzések

- Később érdemes külön rögzíteni, hogy milyen kulcsstruktúrát használ a rendszer.
- A worker és a LiteLLM cache / state együttélését is érdemes dokumentálni.
