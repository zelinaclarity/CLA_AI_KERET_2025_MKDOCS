# Dex

## Cél

A `dex` a rendszer központi OIDC / SSO identity provider komponense.

Feladata:

- központi bejelentkezés biztosítása
- OAuth2 / OpenID Connect tokenek kiadása
- LDAP autentikáció kezelése
- felhasználói csoportok továbbítása
- SSO integráció Grafana / OpenWebUI / egyéb szolgáltatások felé

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

A Dex tipikusan ezekkel kommunikál:

| Szolgáltatás | Funkció             |
| ------------ | ------------------- |
| OpenLDAP     | user backend        |
| Grafana      | OAuth login         |
| OpenWebUI    | SSO                 |
| Traefik      | HTTPS reverse proxy |


## Docker Compose konfiguráció

```bash
  dex:
    image: ghcr.io/dexidp/dex:v2.44.0
    container_name: dex
    restart: unless-stopped
    depends_on:
      - vault-agent
    networks: [ llmnet ]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dex.rule=Host(`${SSO_DOMAIN}`)"
      - "traefik.http.routers.dex.entrypoints=websecure"
      - "traefik.http.routers.dex.tls=true"
      - "traefik.http.services.dex.loadbalancer.server.port=5556"
    ports:
      - "9001:5556"
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        syslog-format: "rfc3164"
        tag: "dex"
    volumes:
      # Template olvasása csak olvashatóként
      - ./dex/config.template.yaml:/etc/dex/config.template.yaml:ro
      # Entrypoint script olvashatóként
      - ./dex/dex-entrypoint.sh:/entry/dex-entrypoint.sh:ro
      # Vault secrets mount
      - vault-secrets:/secrets:ro
      # Dex írási hely a config.yaml-hoz (konténer volume)
      - ./dex/config:/etc/dex/config:rw
    user: root  
    entrypoint: ["/bin/sh", "-c", "apk add --no-cache gettext && /entry/dex-entrypoint.sh"]
```

### Alap tulajdonságok

| Tulajdonság    | Érték                      | Leírás                      |
| -------------- | -------------------------- | --------------------------- |
| Service név    | dex                        | Identity provider service   |
| Image          | ghcr.io/dexidp/dex:v2.44.0 | Dex OpenID Connect provider |
| Konténer név   | dex                        | fix konténer név            |
| Restart policy | unless-stopped             | automatikus újraindítás     |
| Hálózat        | llmnet                     | belső Docker hálózat        |

### Traefik komponensek

| Beállítás                             | Jelentés                         |
| ------------------------------------- | -------------------------------- |
| traefik.enable                        | Traefik publikálás engedélyezése |
| routers.dex.rule                      | domain alapú routing             |
| routers.dex.entrypoints               | HTTPS entrypoint                 |
| routers.dex.tls                       | TLS engedélyezése                |
| services.dex.loadbalancer.server.port | Dex belső portja                 |

### Entrypoint működés

Gettext telepítés, szükséges az envsubst használatához:

entrypoint:
  ["/bin/sh", "-c", "apk add --no-cache gettext && /entry/dex-entrypoint.sh"]
  
### config.template.yaml konfigurációs fájl aktualizálása

Az url-eket aktualizálni kell a domain változása alapján a ..\dex\config.template.yaml fonfigurációs fájlban.
  

