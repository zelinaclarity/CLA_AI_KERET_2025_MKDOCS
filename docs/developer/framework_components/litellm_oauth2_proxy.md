# LiteLLM OAuth2 Proxy

## Cél

A `litellm_oauth2_proxy` a LiteLLM elé helyezett OIDC auth proxy, amely Dex-alapú bejelentkezést és group alapú hozzáférés-szabályozást biztosít.

## Compose szerep

- image: `aiclarity.hu:8443/litellm-oauth2-proxy:1.0`
- container_name: `litellm_oauth2_proxy`
- restart: `unless-stopped`

## Függőségek

- `vault-agent`
- `dex`

## Routing

Traefik route:
- host: `${LITELLM_DOMAIN}`
- target port: `4180`

## Fő konfiguráció

- OIDC issuer: `https://${SSO_DOMAIN}/dex`
- upstream: `http://litellm:4000`
- scope: `openid email profile groups`
- group claim és allowed groups compose env alapján

## Mountok

- `${ROOTCA}:/usr/local/share/ca-certificates/rootCA.crt:ro`
- `./litellm-oauth2-proxy/litellm-oauth-secrets.sh:/litellm-oauth-secrets.sh:ro`
- `vault-secrets:/secrets:ro`

## Fejlesztői megjegyzések

- Külön auth oldalon is hivatkozni érdemes.
- A `litellm-oauth-secrets.sh` script fontos kapcsolódó forrás.
