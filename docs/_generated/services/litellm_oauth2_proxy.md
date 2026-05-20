# litellm_oauth2_proxy

**Image:** `quay.io/oauth2-proxy/oauth2-proxy:v7.6.0`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `OAUTH2_PROXY_PROVIDER` = `oidc`
- `OAUTH2_PROXY_OIDC_ISSUER_URL` = `https://${SSO_DOMAIN}/dex`
- `OAUTH2_PROXY_CLIENT_ID` = `${LITELLM_OAUTH_CLIENT_ID:-litellm}`
- `OAUTH2_PROXY_CLIENT_SECRET` = `${OAUTH2_PROXY_CLIENT_SECRET}`
- `OAUTH2_PROXY_REDIRECT_URL` = `${LITELLM_OAUTH_REDIRECT_URI:-http://localhost:4000/oauth2/callback}`
- `OAUTH2_PROXY_SCOPE` = `openid email profile groups`
- `OAUTH2_PROXY_EMAIL_DOMAINS` = `*`
- `OAUTH2_PROXY_INSECURE_SKIP_EMAIL_VERIFICATION` = `true`
- `OAUTH2_PROXY_COOKIE_SECRET` = `${OAUTH2_PROXY_COOKIE_SECRET}`
- `OAUTH2_PROXY_COOKIE_SECURE` = `false`
- `OAUTH2_PROXY_COOKIE_EXPIRE` = `${SESSION_EXPIRE}`
- `OAUTH2_PROXY_COOKIE_REFRESH` = `0`
- `OAUTH2_PROXY_SESSION_COOKIE_MINIMAL` = `true`
- `OAUTH2_PROXY_UPSTREAMS` = `http://litellm:4000`
- `OAUTH2_PROXY_HTTP_ADDRESS` = `0.0.0.0:4180`
- `OAUTH2_PROXY_OIDC_GROUPS_CLAIM` = `${LITELLM_OIDC_GROUPS_CLAIM:-groups}`
- `OAUTH2_PROXY_ALLOWED_GROUPS` = `${LITELLM_ALLOWED_GROUPS:-llm-admins}`
- `SSL_CERT_FILE` = `/usr/local/share/ca-certificates/rootCA.crt`
- `REQUESTS_CA_BUNDLE` = `/usr/local/share/ca-certificates/rootCA.crt`

## Secrets

- `oauth2_proxy_client_secret` (./secrets/oauth2_proxy_client_secret)
- `oauth2_proxy_cookie_secret` (./secrets/oauth2_proxy_cookie_secret)

## Volumes

- `${ROOTCA}:/usr/local/share/ca-certificates/rootCA.crt:ro`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.litellm.rule=Host(`${LITELLM_DOMAIN}`)`
- `traefik.http.routers.litellm.entrypoints=websecure`
- `traefik.http.routers.litellm.tls=true`
- `traefik.http.services.litellm.loadbalancer.server.port=4180`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `litellm` | `Host(`${LITELLM_DOMAIN}`)` | `websecure` | `true` | `4180` |
