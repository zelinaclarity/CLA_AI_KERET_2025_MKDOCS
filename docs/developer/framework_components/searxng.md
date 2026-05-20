# SearXNG Web Search – Docker konfiguráció

Ez a dokumentáció a **SearXNG** privát metakereső Docker konténer konfigurációját írja le.

A konfiguráció egy **Docker Compose service**, amely egy SearXNG példányt futtat a `llmnet` hálózaton, valamint egy alap **botvédelem** és **beállítási fájl** konfigurációt tartalmaz.

---

# 1. Docker Service konfiguráció

```yaml
# ---------------- SearXNG (Web Search) ----------------
searxng:
  image: searxng/searxng:2026.2.6-b5bb27f23
  container_name: searxng
  restart: unless-stopped

  networks:
    - llmnet

  volumes:
    - ./searxng:/etc/searxng:rw

  ports:
    - "8081:8080"
```

## Magyarázat

| Beállítás      | Jelentés                                                          |
| -------------- | ----------------------------------------------------------------- |
| image          | A SearXNG hivatalos Docker image verziója                         |
| container_name | A futó konténer neve                                              |
| restart        | Automatikus újraindítás ha a konténer leáll                       |
| networks       | A `llmnet` Docker hálózat használata                              |
| volumes        | A helyi `./searxng` mappa mountolása a konténer konfigurációjához |
| ports          | A host `8081` port → konténer `8080` port                         |

A webes felület elérhető:

```
http://localhost:8081
```

---

# 2. limiter.toml konfiguráció

Ez a fájl a **SearXNG bot detection és IP limitáció** beállításait tartalmazza.

```toml
[botdetection.ip_limit]
link_token = false

[botdetection.ip_lists]
block_ip = []
pass_ip = ["127.0.0.1"]
```

## Magyarázat

### botdetection.ip_limit

| Opció      | Jelentés                                                         |
| ---------- | ---------------------------------------------------------------- |
| link_token | Ha `true`, minden keresési linkhez token kerül. Itt kikapcsolva. |

### botdetection.ip_lists

| Opció    | Jelentés                       |
| -------- | ------------------------------ |
| block_ip | Tiltott IP címek listája       |
| pass_ip  | Engedélyezett IP címek listája |

Ebben a konfigurációban:

* **127.0.0.1 mindig engedélyezett**
* nincs blokkolt IP

---

# 3. settings.yml konfiguráció

Ez a SearXNG fő konfigurációs fájlja.

```yaml
use_default_settings: true

server:
  secret_key: "`${SEARXNG_SECRET_KEY}`"

general:
  debug: false

search:
  formats:
    - html
    - json

engines:
  - name: radio browser
    disabled: true
```

## Magyarázat

### use_default_settings

```
true
```

A SearXNG alapértelmezett beállításait használja, amelyeket ez a fájl felülírhat.

---

### server.secret_key

A szerver titkos kulcsa.

Fontos:

* session kezeléshez használja
* production környezetben **random kulcs legyen**

---

### general.debug

```
false
```

* `true` → debug mód
* `false` → production mód

---

### search.formats

Engedélyezett API válaszformátumok.

```
html
json
```

Ez lehetővé teszi:

* böngésző használat
* API használat

Példa:

```
http://localhost:8081/search?q=ai&format=json
```

---

### engines

Keresőmotor konfiguráció.

Ebben a példában a **Radio Browser engine** ki van kapcsolva.

```yaml
- name: radio browser
  disabled: true
```

---

# 4. Könyvtárstruktúra

Ajánlott projekt struktúra:

```
project/
│
├─ docker-compose.yml
│
└─ searxng/
   ├─ settings.yml
   └─ limiter.toml
```

---

# 5. Konténer indítása

```bash
docker compose up -d
```

Konténer állapot ellenőrzése:

```bash
docker ps
```

Logok megtekintése:

```bash
docker logs searxng
```

---

# 6. API használat

Példa keresés JSON válasszal:

```
http://localhost:8081/search?q=openai&format=json
```

---

# 7. Biztonsági ajánlások

Production használatnál ajánlott:

* random `secret_key`
* reverse proxy használata (Nginx / Traefik)
* HTTPS
* rate limit
* authentikáció

---

# 8. Használati esetek

A SearXNG gyakran használható:

* **LLM keresési backendként**
* **RAG rendszerekhez**
* **self-hosted search API**
* **privacy search engine**

---

# Összefoglalás

Ez a konfiguráció:

* Dockerben futtat egy **SearXNG példányt**
* elérhető **8081 porton**
* támogat **HTML és JSON keresést**
* tartalmaz **alap botvédelem konfigurációt**
* letilt egy felesleges keresőmotort.

---
