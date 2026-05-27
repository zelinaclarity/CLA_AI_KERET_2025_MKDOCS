# Traefik

## Cél

A traefik szolgáltatás a rendszer központi reverse proxy és ingress gateway komponense.

Feladata:

- HTTPS forgalom kezelése
- domain alapú routing
- TLS termináció
- Docker service discovery
- belső szolgáltatások publikálása
- dashboard biztosítása

A teljes stack külső belépési pontja.

## Beállítás

- domain routing
- TLS
- middleware-ek

## Docker Compose konfiguráció

```bash
  traefik:
    image: traefik:v3.6.7
    container_name: traefik
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.file.directory=/certs"
      - "--providers.file.watch=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.websecure.http.tls=true"
      - "--serversTransport.insecureSkipVerify=true"
      - "--log.level=INFO"
    ports:
      - "80:80"
      - "443:443"
    logging:
      driver: syslog
      options:
        syslog-address: "udp://127.0.0.1:5514"
        syslog-format: "rfc3164"
        tag: "traefik"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./certs:/certs:ro"
    networks:
      - llmnet
    labels:
      - "traefik.enable=true"
      # Dashboard router
      - "traefik.http.routers.traefik-dash.rule=Host(`${TRAEFIK_DOMAIN}`)"
      - "traefik.http.routers.traefik-dash.entrypoints=websecure"
      - "traefik.http.routers.traefik-dash.tls=true"
      # Dashboard service
      - "traefik.http.routers.traefik-dash.service=api@internal"
```


| Tulajdonság    | Érték          | Leírás                  |
| -------------- | -------------- | ----------------------- |
| Service név    | traefik        | reverse proxy service   |
| Image          | traefik:v3.6.7 | Traefik v3              |
| Konténer név   | traefik        | fix konténer név        |
| Restart policy | unless-stopped | automatikus újraindítás |
| Hálózat        | llmnet         | közös service network   |

## Port mapping

| Host port | Container port | Leírás           |
| --------- | -------------- | ---------------- |
| 80        | 80             | HTTP entrypoint  |
| 443       | 443            | HTTPS entrypoint |

## Command paraméterek

### Dashboard engedélyezése

Bekapcsolja a Traefik webes admin dashboardot.

```bash
--api.dashboard=true
```

### Csak explicit publikált service-ek

```bash
--providers.docker.exposedbydefault=false
```

Csak azok a service-ek jelennek meg, amelyeken: traefik.enable=true

### File provider

Dinamikus konfiguráció és TLS cert kezelés fájlból.

```bash
--providers.file.directory=/certs
--providers.file.watch=true
```

### HTTPS entrypoint

```bash
--entrypoints.websecure.address=:443
--entrypoints.websecure.http.tls=true
```

### Log level

```bash
--log.level=INFO
```

| Szint | Jelentés        |
| ----- | --------------- |
| DEBUG | részletes debug |
| INFO  | normál működés  |
| WARN  | warningok       |
| ERROR | csak hibák      |

### Volume-ok

| Volume      | Cél        | Típus | Leírás            |
| ----------- | ---------- | ----- | ----------------- |
| docker.sock | Docker API | RO    | service discovery |
| ./certs     | /certs     | RO    | TLS certifikátok  |


### Dashboard publikálás

A dashboard elérését a .env fájlban állítjuk be és az alábbi módon hivaktozunk rá:

```bash
traefik.http.routers.traefik-dash.rule=Host(`${TRAEFIK_DOMAIN}`)
```

### certs.yml aktualizálása

../certs mappában találhatók a certificate-ek fontos, hogy ezek elérhetőségét aktualizálni kell a ../certs/certs.yml fájl-ban.

### Traefik által publikált szolgáltatások

A szolgáltatások elérését a .env fájlban állítjuk be és azokat dinamikusan állítjuk be az egyes szolgáltatásoknak.

| Komponens | Domain változó | Belső port | Router név | Path / Rule | TLS | Megjegyzés |
|---|---|---|---|---|---|---|
| Traefik Dashboard | `${TRAEFIK_DOMAIN}` | api@internal | `traefik-dash` | `Host(...)` | Igen | Traefik dashboard |
| MinIO | `${MINIO_DOMAIN}` | 9000 | `minio` | `Host(...)` | Igen | S3 API endpoint |
| Dex | `${SSO_DOMAIN}` | 5556 | `dex` | `Host(...)` | Igen | OIDC / SSO provider |
| OpenWebUI | `${OPENWEBUI_DOMAIN}` | 8080 | `openwebui` | `Host(...)` | Igen | AI chat frontend |
| Docx Service | `${DOCX_API_DOMAIN}` | 8000 | `docx-service` | `Host(...)` | Igen | DOCX/PDF generáló API |
| OpenWebUI Files | `${OPENWEBUI_DOMAIN}` | 8080 | `openwebui-files` | `Host(...) && PathPrefix(/generated-files/)` | Igen | Statikus generált fájlok |
| PWM | `${PASSWD_DOMAIN}` | 8080 | `pwm` | `Host(...)` | Igen | LDAP jelszókezelő |
| LiteLLM OAuth2 Proxy | `${LITELLM_DOMAIN}` | 4180 | `litellm` | `Host(...)` | Igen | OAuth2 védett LiteLLM proxy |
| API Gateway | `${API_GATEWAY_DOMAIN}` | 8080 | `api-gateway` | `Host(...)` | Igen | Külső API gateway |
| Phoenix | `${PHOENIX_DOMAIN}` | 6006 | `phoenix` | `Host(...)` | Igen | Tracing / observability |
| Grafana | `${GRAFANA_DOMAIN}` | 3000 | `grafana` | `Host(...)` | Igen | Monitoring dashboard |

### Globális Traefik konfiguráció

| Beállítás | Érték | Jelentés |
|---|---|---|
| Docker provider | `true` | Docker label alapú discovery |
| exposedByDefault | `false` | Csak explicit engedélyezett service-ek publikusak |
| File provider | `/certs` | TLS/certifikát konfiguráció |
| EntryPoint `web` | `:80` | HTTP |
| EntryPoint `websecure` | `:443` | HTTPS |
| TLS enabled | `true` | HTTPS minden routeren |
| insecureSkipVerify | `true` | Backend TLS cert ellenőrzés kikapcsolva |
| Dashboard API | `true` | Traefik dashboard engedélyezve |
| Log level | `INFO` | Logolási szint |

### Traefik által használt közös label minták

| Label | Funkció |
|---|---|
| `traefik.enable=true` | Service publikálása |
| `traefik.http.routers.<name>.rule` | Host/path routing |
| `traefik.http.routers.<name>.entrypoints=websecure` | HTTPS endpoint használata |
| `traefik.http.routers.<name>.tls=true` | TLS engedélyezése |
| `traefik.http.services.<name>.loadbalancer.server.port` | Konténer belső portja |


### Speciális Traefik konfigurációk

| Komponens | Speciális beállítás |
|---|---|
| `openwebui-files` | `priority=100` a path routing prioritás miatt |
| `litellm_oauth2_proxy` | Custom header middleware (`X-Forwarded-Proto=https`) |
| `traefik` | `api@internal` service használata dashboardhoz |
| `grafana` | OIDC mögötti reverse proxy működés |
| `dex` | OIDC identity provider szolgáltatás |