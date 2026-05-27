# API Gateway

## Cél

Az `api-gateway` egy saját buildelt komponens, amely a LiteLLM fölé ülő API gateway szerepet tölti be.

## Compose szerep

- build: `./api-gateway`
- container_name: `api-gateway`
- restart: `unless-stopped`

## Függőségek

- `litellm`

## Környezeti változók

- `UPSTREAM=http://litellm:4000`
- `TIMEOUT_S=120`
- `TZ=Europe/Budapest`

## Routing

Traefik route:
- host: `${API_GATEWAY_DOMAIN}`
- target port: `8080`

## Fejlesztői megjegyzések

- Mivel saját buildből készül, ez különösen fontos fejlesztői dokumentációs pont.
- Külön részletezni kell:
  - API felület,
  - timeout / retry stratégia,
  - upstream hiba kezelés.
