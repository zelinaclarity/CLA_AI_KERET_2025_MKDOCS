# api-gateway

**Build:** `./api-gateway`

## Depends on

- `litellm`

## Environment

- `UPSTREAM` = `http://litellm:4000`
- `TIMEOUT_S` = `120`
- `TZ` = `Europe/Budapest`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.api-gateway.rule=Host(`${API_GATEWAY_DOMAIN}`)`
- `traefik.http.routers.api-gateway.entrypoints=websecure`
- `traefik.http.routers.api-gateway.tls=true`
- `traefik.http.services.api-gateway.loadbalancer.server.port=8080`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `api-gateway` | `Host(`${API_GATEWAY_DOMAIN}`)` | `websecure` | `true` | `8080` |
