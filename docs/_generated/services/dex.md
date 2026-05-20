# dex

**Image:** `ghcr.io/dexidp/dex:v2.44.0`

## Ports

- `9001:5556`

## Volumes

- `./dex/config.yaml:/etc/dex/config.yaml:ro`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.dex.rule=Host(`${SSO_DOMAIN}`)`
- `traefik.http.routers.dex.entrypoints=websecure`
- `traefik.http.routers.dex.tls=true`
- `traefik.http.services.dex.loadbalancer.server.port=5556`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `dex` | `Host(`${SSO_DOMAIN}`)` | `websecure` | `true` | `5556` |
