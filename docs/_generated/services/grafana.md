# grafana

**Image:** `grafana/grafana:12.3.1`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `GF_SERVER_ROOT_URL` = `https://${GRAFANA_DOMAIN}`
- `GF_USERS_ALLOW_SIGN_UP` = `false`
- `GF_AUTH_DISABLE_LOGIN_FORM` = `true`
- `GF_AUTH_BASIC_ENABLED` = `false`
- `GF_AUTH_GENERIC_OAUTH_ENABLED` = `true`
- `GF_AUTH_GENERIC_OAUTH_NAME` = `${SSO_PROVIDER_NAME:-Comp SSO}`
- `GF_AUTH_GENERIC_OAUTH_CLIENT_ID` = `grafana`
- `GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET` = `${GRAFANA_OAUTH_CLIENT_SECRET}`
- `GF_AUTH_GENERIC_OAUTH_SCOPES` = `openid profile email groups`
- `GF_AUTH_GENERIC_OAUTH_AUTH_URL` = `https://${SSO_DOMAIN}/dex/auth`
- `GF_AUTH_GENERIC_OAUTH_TOKEN_URL` = `http://dex:5556/dex/token`
- `GF_AUTH_GENERIC_OAUTH_API_URL` = `http://dex:5556/dex/userinfo`
- `GF_AUTH_GENERIC_OAUTH_GROUPS_ATTRIBUTE_PATH` = `groups`
- `GF_AUTH_GENERIC_OAUTH_ALLOWED_GROUPS` = `${GRAFANA_ALLOWED_GROUPS}`
- `GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_PATH` = `contains(groups[*], '${GRAFANA_ALLOWED_GROUPS}') && 'GrafanaAdmin' || 'None'`
- `GF_AUTH_GENERIC_OAUTH_ALLOW_ASSIGN_GRAFANA_ADMIN` = `true`
- `GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_STRICT` = `true`
- `GF_AUTH_GENERIC_OAUTH_AUTH_STYLE` = `InHeader`
- `GF_AUTH_LOGIN_MAXIMUM_LIFETIME_DURATION` = `${SESSION_EXPIRE}`
- `GF_AUTH_LOGIN_MAXIMUM_INACTIVE_LIFETIME_DURATION` = `${SESSION_EXPIRE}`
- `GF_AUTH_TOKEN_ROTATION_INTERVAL_MINUTES` = `1`

## Volumes

- `grafana_data:/var/lib/grafana`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.grafana.rule=Host(`${GRAFANA_DOMAIN}`)`
- `traefik.http.routers.grafana.entrypoints=websecure`
- `traefik.http.routers.grafana.tls=true`
- `traefik.http.services.grafana.loadbalancer.server.port=3000`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `grafana` | `Host(`${GRAFANA_DOMAIN}`)` | `websecure` | `true` | `3000` |
