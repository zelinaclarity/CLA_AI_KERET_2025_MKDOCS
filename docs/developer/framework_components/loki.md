# Loki – Log Aggregációs Rendszer

A **Loki** a Grafana által fejlesztett **log aggregációs rendszer**, amely konténer és alkalmazás logok gyűjtésére, tárolására és lekérdezésére szolgál. A Loki egyik fő előnye, hogy **Prometheus-szerű label alapú indexelést használ**, így hatékonyabb és olcsóbb log tárolást tesz lehetővé.

A rendszer tipikusan **Promtail, Fluentbit vagy Grafana Agent** segítségével gyűjti a logokat.

---

# Loki célja

A Loki célja, hogy:

* központi log tárolást biztosítson
* hatékony log lekérdezést adjon
* minimalizálja az index méretét
* jól integrálódjon a **Grafana stackkel**

---

# Loki architektúra

```
Application / Containers
           │
           ▼
        Promtail
           │
           ▼
           Loki
           │
           ▼
        Grafana
```

### Komponensek

| Komponens | Feladat                     |
| --------- | --------------------------- |
| Promtail  | log collector               |
| Loki      | log storage és query engine |
| Grafana   | vizualizáció                |

---

# Docker konfiguráció

A Loki konténer Docker Compose segítségével fut.

```yaml
loki:
  image: grafana/loki:3.0.0
  container_name: loki
  restart: unless-stopped
  networks: [ llmnet ]
  command: -config.file=/etc/loki/config.yml
  volumes:
    - ./loki/config.yml:/etc/loki/config.yml:ro
    - loki_data:/loki
```

## Magyarázat

| Paraméter | Jelentés            |
| --------- | ------------------- |
| image     | Loki Docker image   |
| command   | konfigurációs fájl  |
| volumes   | config + storage    |
| restart   | automatikus restart |

---

# Loki konfiguráció

A Loki működését a **config.yml** fájl határozza meg.

---

# Authentication

```yaml
auth_enabled: false
```

Ez kikapcsolja az autentikációt.

Tipikusan **internal hálózaton** használják így.

---

# Server beállítás

```yaml
server:
  http_listen_port: 3100
```

A Loki API ezen a porton érhető el.

```
http://localhost:3100
```

---

# Common konfiguráció

```yaml
common:
  path_prefix: /loki
  replication_factor: 1
```

### path_prefix

A Loki adatainak tárolási könyvtára.

```
/loki
```

### replication_factor

A log adatok replikációja.

| Érték | Jelentés    |
| ----- | ----------- |
| 1     | single node |
| 3     | HA cluster  |

---

# Storage

A Loki ebben a konfigurációban **filesystem storage-t** használ.

```yaml
storage:
  filesystem:
    chunks_directory: /loki/chunks
```

### Chunk

A Loki a logokat **chunkokban** tárolja.

Chunk = log blokkok.

---

# Schema konfiguráció

```yaml
schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
```

### store: tsdb

A Loki **TSDB (Time Series Database)** indexet használ.

### schema: v13

Az aktuális Loki storage schema.

---

# Index konfiguráció

```yaml
index:
  prefix: index_
  period: 24h
```

### prefix

Index fájl neve.

```
index_YYYYMMDD
```

### period

Index rotáció.

```
24h
```

---

# Storage config

```yaml
storage_config:
  filesystem:
    directory: /loki/chunks
```

Ez a log chunk fájlok helye.

---

# TSDB Shipper

```yaml
tsdb_shipper:
  active_index_directory: /loki/index
  cache_location: /loki/index_cache
  cache_ttl: 24h
```

### active_index_directory

Aktív index.

### cache_location

Index cache.

### cache_ttl

Cache élettartam.

---

# Limits konfiguráció

```yaml
limits_config:
  retention_period: 720h
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
  max_streams_per_user: 0
  max_line_size: 0
```

### retention_period

Log retention.

```
720h = 30 nap
```

### ingestion_rate_mb

Max log ingest sebesség.

```
10 MB / sec
```

### ingestion_burst_size_mb

Burst ingest limit.

```
20 MB
```

### max_streams_per_user

Stream limit.

```
0 = unlimited
```

---

# Compactor

A compactor felel a **régi logok törléséért és chunk összevonásáért**.

```yaml
compactor:
  working_directory: /loki/compactor
  retention_enabled: true
  delete_request_store: filesystem
```

### retention_enabled

Engedélyezi a retention policy-t.

---

# Loki API

### Health check

```
/ready
```

### Metrics

```
/metrics
```

### Push logs

```
/loki/api/v1/push
```

---

# Log lekérdezés

A Loki **LogQL** lekérdezési nyelvet használ.

### Példa

```
{container="api"}
```

### Szűrés

```
{container="api"} |= "error"
```

### Regex

```
{container="api"} |~ "timeout|failed"
```

---

# Loki előnyei

| Előny                 | Magyarázat       |
| --------------------- | ---------------- |
| kis index             | csak label index |
| olcsó storage         | chunk alapú      |
| Grafana integráció    | natív            |
| horizontális skálázás | cluster support  |

---

# Tipikus use case

* Docker log monitoring
* Kubernetes logging
* microservice debugging
* audit log storage
* AI / LLM platform logging

---

# Összegzés

A Loki egy **hatékony, skálázható log aggregációs rendszer**, amely ideális:

* konténer infrastruktúrákhoz
* microservice architektúrákhoz
* Grafana monitoring stackhez

Ebben a konfigurációban:

* filesystem storage
* TSDB index
* 30 nap retention
* single node deployment



# Loki – Tipikus hibák és gyors ellenőrzések

Ez a dokumentum a **Loki log aggregációs rendszer** gyakori hibáit és azok gyors ellenőrzési módját mutatja be. Segítségével gyorsan diagnosztizálható, ha a log pipeline nem működik megfelelően.

---

# 1. Loki nem indul el

## Tünetek

* a Loki container azonnal kilép
* `docker ps` nem mutatja futó állapotban
* Grafana vagy Promtail nem éri el

## Ellenőrzés

```bash
docker logs loki
```

### Gyakori okok

| Ok               | Magyarázat                |
| ---------------- | ------------------------- |
| hibás config.yml | YAML szintaxis hiba       |
| hiányzó volume   | Loki nem tud írni         |
| rossz file path  | config file nem található |

## Gyors teszt

```bash
docker exec -it loki ls /etc/loki
```

---

# 2. Loki nem érhető el HTTP-n

## Tünetek

* Grafana nem tud csatlakozni
* Promtail push error
* `connection refused`

## Ellenőrzés

```bash
curl http://localhost:3100/ready
```

### Várt válasz

```json
ready
```

## Container port ellenőrzés

```bash
docker ps
```

Ha nincs 3100 port:

```bash
docker logs loki
```

---

# 3. Promtail nem tud logot küldeni

## Tünetek

Promtail log:

```
error sending batch
connection refused
```

## Ellenőrzés

```bash
docker logs promtail
```

### Gyakori okok

| Ok                     | Megoldás           |
| ---------------------- | ------------------ |
| rossz Loki URL         | `http://loki:3100` |
| hálózat hiba           | docker network     |
| Loki container nem fut | restart            |

## Teszt

Promtail containerből:

```bash
curl http://loki:3100/ready
```

---

# 4. Nincsenek logok Loki-ban

## Tünetek

Grafana query üres.

```
{container="api"}
```

nem ad vissza logot.

## Ellenőrzés

Promtail log:

```bash
docker logs promtail
```

Keresd:

```
scraping target
```

Ha nincs ilyen:

Promtail nem talál log forrást.

---

# 5. Docker log path hiba

Promtail gyakran nem találja a Docker log fájlokat.

## Ellenőrzés

```bash
ls /var/lib/docker/containers
```

Ha nincs mount:

Promtail config hibás.

### Szükséges mount

```yaml
- /var/lib/docker/containers:/var/lib/docker/containers:ro
```

---

# 6. Loki storage nem működik

## Tünetek

Loki log:

```
error writing chunk
```

## Ellenőrzés

```bash
docker exec -it loki ls /loki
```

### Elvárt könyvtárak

```
chunks
index
index_cache
rules
```

---

# 7. Log retention nem működik

## Tünet

A logok nem törlődnek.

## Ellenőrzés

```yaml
limits_config:
  retention_period: 720h
```

és

```yaml
compactor:
  retention_enabled: true
```

---

# 8. Loki túl sok memóriát használ

## Tünet

* magas RAM
* container OOM

## Ellenőrzés

```bash
docker stats
```

### Gyakori ok

| Ok              | Magyarázat       |
| --------------- | ---------------- |
| túl sok label   | high cardinality |
| túl nagy ingest | túl sok log      |

---

# 9. Label explosion

A Loki egyik leggyakoribb teljesítmény problémája.

## Példa

Rossz label:

```
request_id
user_id
timestamp
```

Ez **milliónyi log streamet generál**.

## Ajánlott label

```
service
container
level
environment
```

---

# 10. Loki API teszt

Egyszerű push teszt:

```bash
curl -X POST http://localhost:3100/loki/api/v1/push \
-H "Content-Type: application/json" \
-d '{
"streams": [
  {
    "stream": { "service": "test" },
    "values": [
      ["'"$(date +%s%N)"'", "hello loki"]
    ]
  }
]
}'
```

---

# Gyors diagnosztikai parancsok

## Loki health

```bash
curl localhost:3100/ready
```

## Loki metrics

```bash
curl localhost:3100/metrics
```

## Loki log

```bash
docker logs loki
```

## Promtail log

```bash
docker logs promtail
```

## Docker container list

```bash
docker ps
```

---

# Gyors ellenőrzési checklist

| Ellenőrzés      | Parancs                      |
| --------------- | ---------------------------- |
| Loki fut        | `docker ps`                  |
| Loki health     | `curl localhost:3100/ready`  |
| Loki log        | `docker logs loki`           |
| Promtail log    | `docker logs promtail`       |
| Docker log path | `/var/lib/docker/containers` |
| Storage mount   | `/loki`                      |

---

# Ajánlott monitorozás

A Loki működésének figyeléséhez ajánlott:

* **Grafana**
* **Prometheus**
* Loki metrics dashboard

---

# Összegzés

A Loki hibák többsége az alábbi területekhez kapcsolódik:

* hibás konfiguráció
* storage problémák
* network hiba
* log pipeline hibák
* label explosion

A fenti gyors ellenőrzések segítségével a legtöbb probléma **néhány perc alatt diagnosztizálható**.
