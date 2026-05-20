# pwm

**Image:** `fjudith/pwm:latest`

## Environment

- `TZ=${TZ:-Europe/Budapest}`
- `PWM_APPLICATIONFLAGS=NoFileLock`

## Volumes

- `pwm-data:/usr/share/pwm`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.pwm.rule=Host(`${PASSWD_DOMAIN}`)`
- `traefik.http.routers.pwm.entrypoints=websecure`
- `traefik.http.routers.pwm.tls=true`
- `traefik.http.services.pwm.loadbalancer.server.port=8080`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `pwm` | `Host(`${PASSWD_DOMAIN}`)` | `websecure` | `true` | `8080` |
