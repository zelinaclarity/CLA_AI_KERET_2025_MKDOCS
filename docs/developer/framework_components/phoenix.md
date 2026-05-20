# Phoenix

## Cél

A `phoenix` observability / tracing komponens.

## Compose szerep

- image: `arizephoenix/phoenix:latest`
- container_name: `phoenix`

## Portok

- `6006:6006`
- `4317:4317`
- `4318:4318`

## Környezeti változók

- `PHOENIX_PORT=6006`

## Kapcsolódó komponensek

- `litellm` a compose alapján ide küld tracing adatot.

## Fejlesztői megjegyzések

- Az observability architektúrában külön fejezetet érdemel.
