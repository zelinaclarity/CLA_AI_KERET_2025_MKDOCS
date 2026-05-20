# traefik

**Image:** `traefik:v3.6.7`

## Ports

- `80:80`
- `443:443`

## Volumes

- `/var/run/docker.sock:/var/run/docker.sock:ro`
- `./certs:/certs:ro`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.traefik-dash.rule=Host(`${TRAEFIK_DOMAIN}`)`
- `traefik.http.routers.traefik-dash.entrypoints=websecure`
- `traefik.http.routers.traefik-dash.tls=true`
- `traefik.http.routers.traefik-dash.service=api@internal`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `traefik-dash` | `Host(`${TRAEFIK_DOMAIN}`)` | `websecure` | `true` | `` |
