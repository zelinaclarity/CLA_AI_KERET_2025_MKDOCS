# Dex

## Cél

A `dex` a rendszer központi OIDC / SSO identity provider komponense.

## Compose szerep

- image: `ghcr.io/dexidp/dex:v2.44.0`
- container_name: `dex`
- restart: `unless-stopped`

## Függőségek

- `vault-agent`

## Portok

- `9001:5556`

## Routing

Traefik route:
- host: `${SSO_DOMAIN}`
- target port: `5556`

## Mountok

- `./dex/config.template.yaml:/etc/dex/config.template.yaml:ro`
- `./dex/dex-entrypoint.sh:/entry/dex-entrypoint.sh:ro`
- `vault-secrets:/secrets:ro`
- `./dex/config:/etc/dex/config:rw`

## Indítási logika

A service root userrel indul, telepíti a `gettext` csomagot, majd a `dex-entrypoint.sh` script állítja elő / kezeli a konfigurációt.

## Kapcsolódó komponensek

- `openwebui`
- `grafana`
- `litellm_oauth2_proxy`

## Fejlesztői megjegyzések

- Ez a service külön auth/SSO fejezetbe is tartozik.
- Kapcsolódó fájlok:
  - `dex/config.template.yaml`
  - `dex/dex-entrypoint.sh`
  - `dex/config/*`
