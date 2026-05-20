
# OpenWebUI – teljes rendszerleírás

## Áttekintés

Az **OpenWebUI** a rendszer központi felhasználói felülete, amely:

- LLM-ekhez biztosít webes UI-t  
- OIDC/SSO alapú hitelesítést használ (Dex)  
- LiteLLM-en keresztül éri el a modelleket  
- Web search-et integrál (SearXNG)  
- Role és group alapú jogosultságkezelést biztosít  
- Teljesen konténerizált (Docker Compose)  

---

## Architektúra

User → Traefik → OpenWebUI → LiteLLM → modellek  
                    ↓  
                   Dex (SSO)  
                    ↓  
                PostgreSQL  
                    ↓  
                SearXNG (search)  

Kiegészítő komponensek:

- Vault Agent → secret management  
- Valkey (Redis) → cache  
- RAG stack → embedding + retrieval  
- Grafana + Loki → monitoring  
- Central logger → syslog  

---

# OpenWebUI szolgáltatás

## Alap adatok

- **Image**: ghcr.io/open-webui/open-webui:v0.7.2  
- **Port**: 8080  
- **Restart policy**: unless-stopped  
- **Network**: llmnet  

---

## Függőségek

- openwebui_db – PostgreSQL adatbázis  
- dex – OIDC / SSO provider  
- vault-agent – secret injection  

---

## Elérés

### Direkt
http://localhost:8080  

### Éles
https://${OPENWEBUI_DOMAIN}  

---

# Auth / SSO működés

## Alapelv

- nincs lokális login  
- minden auth Dex-en keresztül  

## Tiltások

ENABLE_SIGNUP=false  
ENABLE_PASSWORD_AUTH=false  
ENABLE_LOGIN_FORM=false  

## Engedélyezett

ENABLE_OAUTH_SIGNUP=true  

---

## OIDC konfiguráció

- Provider: Dex  
- Endpoint: http://dex:5556/dex/.well-known/openid-configuration  
- Scope: openid email profile groups  
- Redirect URI: ${OPENWEBUI_OIDC_REDIRECT_URI}  

---

## Role és group kezelés

- claim: groups  
- admin role: llm-admins  
- allowed roles: ai-basic, ai-advanced, llm-admins  

---

# Web search integráció

- engine: searxng  
- endpoint: http://searxng:8080/search?q=<query>&format=json  
- language: hu-HU  

---

# LiteLLM integráció

Az OpenWebUI nem közvetlenül modelleket hív.

LiteLLM biztosítja:

- egységes API  
- model routing  
- proxy  
- logging  

---

# Adatbázis

- PostgreSQL 16  
- DB: openwebui  
- user: admin  

Password:

POSTGRES_PASSWORD_FILE=/secrets/openwebui_db_password  

---

# Persistencia

openwebui-data:/app/backend/data  

Tartalom:

- user adatok  
- chat history  
- config  

---

# Secrets kezelés

## Flow

1. Vault Agent letölti  
2. /secrets volume-ba ír  
3. entrypoint script feldolgozza  

## Entrypoint

/entry/openwebui.secrets-entrypoint.sh  

Feladata:

- env generálás  
- secret load  
- app start  

---

# Branding

Mountok:

- custom.css  
- custom.js  
- index.html  
- logo  
- favicon  
- splash  
- model-map.json  

---

# TLS / CA

Custom CA:

${ROOTCA}:/usr/local/share/ca-certificates/rootCA.crt  

Env:

SSL_CERT_FILE  
REQUESTS_CA_BUNDLE  

---

# Logging

- syslog  
- udp://127.0.0.1:5514  
- tag: openwebui  

---

# Network

llmnet (external)  
subnet: 172.22.0.0/16  

---

# Traefik

Host(${OPENWEBUI_DOMAIN})  
TLS=true  

Funkció:

- HTTPS  
- routing  
- service discovery  

---

# Extra

extra_hosts:

${SSO_DOMAIN}:host-gateway  

---

# Üzemeltetési checklist

## Kötelező

- Vault működik  
- Secretek léteznek  
- Dex működik  
- SearXNG elérhető  
- Traefik működik  

## Ajánlott

- log level nem DEBUG  
- backup  
- healthcheck  
- rate limit  

---

# Összefoglaló

- frontend + auth entrypoint  
- SSO-only  
- LiteLLM mögött  
- search + RAG  
- enterprise stack  

