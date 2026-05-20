# openwebui

**Image:** `ghcr.io/open-webui/open-webui:v0.7.2`

## Depends on

- `openwebui_db`
- `dex`

## Ports

- `8080:8080`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `WEBUI_NAME` = `${OPENWEBUI_NAME:-OpenWebUI}`
- `GLOBAL_LOG_LEVEL` = `INFO`
- `OPENAI_LOG_LEVEL` = `INFO`
- `MAIN_LOG_LEVEL` = `INFO`
- `MODELS_LOG_LEVEL` = `INFO`
- `JWT_EXPIRES_IN` = `${SESSION_EXPIRE}`
- `ENABLE_LDAP` = `false`
- `ENABLE_OAUTH_PERSISTENT_CONFIG` = `false`
- `ENABLE_OAUTH_SIGNUP` = `true`
- `ENABLE_SIGNUP` = `false`
- `ENABLE_PASSWORD_AUTH` = `false`
- `ENABLE_LOGIN_FORM` = `false`
- `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` = `true`
- `OAUTH_PROVIDER_NAME` = `${SSO_PROVIDER_NAME:-Comp SSO}`
- `OPENID_PROVIDER_URL` = `http://dex:5556/dex/.well-known/openid-configuration`
- `OAUTH_CLIENT_ID` = `${OPENWEBUI_OAUTH_CLIENT_ID:-openwebui}`
- `OAUTH_SCOPES` = `openid email profile groups`
- `OPENID_REDIRECT_URI` = `${OPENWEBUI_OIDC_REDIRECT_URI}`
- `ENABLE_OAUTH_ROLE_MANAGEMENT` = `true`
- `OAUTH_ROLES_CLAIM` = `${OPENWEBUI_ROLES_CLAIM:-groups}`
- `OAUTH_ADMIN_ROLES` = `${OPENWEBUI_ADMIN_ROLES:-llm-admins}`
- `OAUTH_ALLOWED_ROLES` = `${OPENWEBUI_ALLOWED_ROLES:-ai-basic,ai-advanced,llm-admins}`
- `ENABLE_OAUTH_GROUP_MANAGEMENT` = `true`
- `OAUTH_GROUP_CLAIM` = `${OPENWEBUI_GROUP_CLAIM:-groups}`
- `ENABLE_OAUTH_GROUP_CREATION` = `true`
- `ENABLE_FORWARD_USER_INFO_HEADERS` = `true`
- `ENABLE_WEB_SEARCH` = `true`
- `WEB_SEARCH_ENGINE` = `searxng`
- `SEARXNG_QUERY_URL` = `http://searxng:8080/search?q=<query>&format=json`
- `SEARXNG_LANGUAGE` = `hu-HU`
- `SSL_CERT_FILE` = `/etc/ssl/certs/ca-certificates.crt`
- `REQUESTS_CA_BUNDLE` = `/etc/ssl/certs/ca-certificates.crt`

## Secrets

- `openwebui_db_password` (./secrets/openwebui_db_password)
- `oauth_client_secret` (./secrets/oauth_client_secret)
- `webui_secret_key` (./secrets/webui_secret_key)

## Volumes

- `openwebui-data:/app/backend/data`
- `./openwebui.secrets-entrypoint.sh:/entry/openwebui.secrets-entrypoint.sh:ro`
- `${ROOTCA}:/usr/local/share/ca-certificates/rootCA.crt:ro`

## Labels

- `traefik.enable=true`
- `traefik.http.routers.openwebui.rule=Host(`${OPENWEBUI_DOMAIN}`)`
- `traefik.http.routers.openwebui.entrypoints=websecure`
- `traefik.http.routers.openwebui.tls=true`
- `traefik.http.services.openwebui.loadbalancer.server.port=8080`

## Traefik routing

| Router | Rule | Entrypoints | TLS | LB port |
|---|---|---|---|---|
| `openwebui` | `Host(`${OPENWEBUI_DOMAIN}`)` | `websecure` | `true` | `8080` |
