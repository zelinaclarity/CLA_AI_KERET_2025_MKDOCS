# Promtail összefoglaló (Docker Compose + config alapján)

A **Promtail** egy log-gyűjtő agent a Grafana Loki ökoszisztémában. A feladata, hogy a futó konténerek logjait **felkutassa**, **beolvassa**, **feldolgozza (pipeline)**, majd **Loki-ba továbbítsa**.

Ebben a stack-ben a Promtail **Docker service discovery**-t használ, ezért automatikusan megtalálja a konténereket a Docker socketen keresztül, és a Docker által írt **json-file** logokat olvassa.

---

## Szerepe

A compose fájlban a Promtail:

* **a host Docker socketét** (`/var/run/docker.sock`) olvassa, hogy lássa a konténereket
* **a host Docker konténer log fájljait** (`/var/lib/docker/containers/...-json.log`) olvassa
* az olvasott logokat **Loki-ba** pusholja a belső hálózaton (`http://loki:3100`)
* a feldolgozás során **címkéket (labels)** ad a logokhoz (container, image, compose_* és level)

---

## Docker Compose szolgáltatás (mit jelent a beállítás)

```yaml
promtail:
  image: grafana/promtail:3.0.0
  container_name: promtail
  restart: unless-stopped
  networks: [ llmnet ]
  command: -config.file=/etc/promtail/config.yml
  volumes:
    - ./promtail/config.yml:/etc/promtail/config.yml:ro
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - promtail_data:/tmp
  depends_on:
      - loki
```

### Kulcspontok

* `depends_on: loki`
  Indítási sorrendet ad (Loki előbb indul), de nem “health check” alapú.

* `./promtail/config.yml -> /etc/promtail/config.yml (ro)`
  A Promtail konfiguráció kívülről, read-only.

* `/var/run/docker.sock (ro)`
  Kell a **docker_sd_configs** discovery-hez (konténer metaadatok: név, image, compose label stb.).

* `/var/lib/docker/containers (ro)`
  Itt vannak a Docker json-file logok. Promtail innen olvas.

* `promtail_data:/tmp`
  Itt tárolja a Promtail a **positions** fájlt (hogy ne olvassa újra a logokat restart után).

---

## Konfiguráció összefoglaló (config.yml alapján)

### 1) Saját HTTP endpoint

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0
```

* A Promtail futtat egy HTTP szervert a metrikák/állapot számára (pl. Grafana/Prometheus monitorozásnál hasznos).

### 2) Positions (log olvasási pozíciók)

```yaml
positions:
  filename: /tmp/positions.yaml
```

* Ez akadályozza meg, hogy restart után a Promtail **visszaolvassa** a korábbi logokat.
* Mivel `/tmp` volume-on van, a positions perzisztens marad.

### 3) Loki kliens (hova pushol)

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
```

* A Promtail ide küldi a log batch-eket.
* A `loki` hostnév a compose network DNS-e (llmnet).

---

## Log forrás: Docker service discovery + json-file logok

### Discovery

```yaml
docker_sd_configs:
  - host: unix:///var/run/docker.sock
    refresh_interval: 5s
```

* 5 másodpercenként frissíti a konténer listát és metaadatokat.

### Log path beállítás

```yaml
- source_labels: [__meta_docker_container_id]
  target_label: __path__
  replacement: /var/lib/docker/containers/$1/$1-json.log
```

* A konténer ID alapján számolja ki, melyik log fájlt olvassa.

---

## Label-ek (címkék), amiket Loki-ban is látni fogsz

A relabeling alapján a Promtail tipikusan az alábbi label-eket teszi rá a log streamre:

* `container` – konténer neve (levágva az elejéről a `/`)
* `image` – docker image
* `compose_project` – compose project label (ha van)
* `compose_service` – compose service label (ha van)
* `level` – log szint (a pipeline állítja elő)

Ezek a label-ek kulcsfontosságúak Loki/Grafana oldalon a keresésekhez, pl.:

* `{container="openwebui"}`
* `{compose_service="litellm"} |= "error"`

---

## Pipeline: hogyan lesz “level” címke a logokból

A pipeline célja: **log level kinyerés + normalizálás + labelként ráírás**.

### 1) Docker stage

```yaml
- docker: {}
```

* A Docker json-file driver formátumát “szétszedi” (üzenet + timestamp kezelése).

### 2) A) JSON alapú level kinyerés

A pipeline megpróbálja JSON-ból megtalálni a level mezőket (többféle névvel is):

* `level`, `lvl`, `severity`, `log_level`, `loglevel`
* nested: `log.level`

Majd:

* kisbetűsít
* normalizál: `warning -> warn`, `critical -> error`
* csak ismert értéket enged labelbe: `trace|debug|info|warn|error|fatal|panic`

### 3) B) Szöveges / logfmt jellegű sorokból

Regex-szel keres pl. ilyet:

* `level=INFO`
* `severity: ERROR`

Majd ugyanúgy normalizál és címkézi.

### 4) C) Default

Ha semmi nem talált:

* `level = unknown`

---

## Mit jelent ez a stack szintjén

A te környezetedben több konténer **syslog driverrel** küldi a logokat a `central-logger` (rsyslog) felé, viszont a Promtail ebben a konfigurációban **a Docker json-file logokat** olvassa.

Ez gyakorlatban azt jelenti:

* **Promtail csak azokat a logokat fogja látni, amik ténylegesen a Docker json-file-ba kerülnek.**
* Ha egy service `logging: driver: syslog`, akkor a json-file logja jellemzően nem (vagy nem ugyanúgy) töltődik → Promtail/Loki oldalon “hiányzó logok” érzete lehet.
* Emiatt a logging architektúrában két párhuzamos csatorna van:

  * syslog → central-logger (rsyslog)
  * json-file → promtail → loki

*(Ha a cél az, hogy minden syslog-os log is menjen Loki-ba, akkor vagy a Promtailt kell syslog/rsyslog file source-ra állítani, vagy az rsyslog-ot Loki irányba továbbítani, vagy a konténereket json-file-ra egységesíteni.)*

---

## Gyors ellenőrzés (hasznos mini-checklist)

* Promtail fut-e?
  `docker ps | grep promtail`

* Loki elérhető-e promtailból?
  `docker exec -it promtail curl -s http://loki:3100/ready`

* Látja-e a docker socketet?
  `docker exec -it promtail ls -l /var/run/docker.sock`

* Látja-e a docker log pathot?
  `docker exec -it promtail ls /var/lib/docker/containers | head`

* Positions megvan-e?
  `docker exec -it promtail cat /tmp/positions.yaml`

---

## Rövid összegzés

A Promtail ebben a stack-ben:

* **Docker discovery**-val konténereket talál
* **json-file** Docker logokat olvas a hostról
* Loki felé pushol (`/loki/api/v1/push`)
* a logokhoz hasznos címkéket ad (container/image/compose_*), és automatikusan előállít egy **level** labelt JSON vagy szöveges minták alapján, különben `unknown`.



# Promtail – Tipikus hibák és gyors ellenőrzések

Ez a dokumentum a **Promtail log collector** gyakori hibáit és azok gyors ellenőrzési módszereit mutatja be. A Promtail feladata, hogy logokat gyűjtsön különböző forrásokból (pl. Docker konténerekből) és továbbítsa azokat **Loki** felé.

A legtöbb Promtail probléma a következő kategóriákba tartozik:

* Loki kapcsolat hiba
* log forrás nem található
* konfigurációs hiba
* Docker socket vagy log path probléma
* pipeline parsing hiba

---

# 1. Promtail nem indul el

## Tünetek

* a container azonnal kilép
* `docker ps` nem mutatja futó állapotban
* nincs log Loki-ban

## Ellenőrzés

```bash
docker logs promtail
```

### Gyakori okok

| Ok                | Magyarázat                   |
| ----------------- | ---------------------------- |
| hibás YAML        | config szintaxis hiba        |
| rossz config path | config file nem található    |
| permission hiba   | nem tud log fájlokat olvasni |

---

# 2. Promtail nem tud csatlakozni Loki-hoz

## Tünet

Promtail log:

```
error sending batch
connection refused
```

## Ellenőrzés

Promtail containerből:

```bash
curl http://loki:3100/ready
```

### Gyakori okok

| Ok                     | Megoldás           |
| ---------------------- | ------------------ |
| Loki container nem fut | indítsd újra       |
| rossz URL              | `http://loki:3100` |
| hálózat hiba           | docker network     |

---

# 3. Promtail nem talál log forrásokat

## Tünetek

Promtail logban nincs scraping információ.

```
scraping target
```

nem jelenik meg.

## Ellenőrzés

```bash
docker logs promtail
```

Ha nem látod a következőt:

```
adding target
```

akkor a log discovery nem működik.

---

# 4. Docker socket nincs mountolva

Promtail Docker service discovery használ.

## Szükséges mount

```yaml
- /var/run/docker.sock:/var/run/docker.sock:ro
```

## Ellenőrzés

```bash
docker exec -it promtail ls /var/run
```

Ha nincs `docker.sock`, akkor a discovery nem működik.

---

# 5. Docker log path nem érhető el

Promtail a Docker JSON log fájlokat olvassa.

## Log path

```
/var/lib/docker/containers/<container-id>/<container-id>-json.log
```

## Szükséges mount

```yaml
- /var/lib/docker/containers:/var/lib/docker/containers:ro
```

## Ellenőrzés

```bash
docker exec -it promtail ls /var/lib/docker/containers
```

---

# 6. Loki push hibák

## Tünet

Promtail log:

```
server returned HTTP status 400
```

vagy

```
server returned HTTP status 500
```

## Ellenőrzés

```bash
docker logs promtail
```

### Gyakori okok

| Ok                | Magyarázat      |
| ----------------- | --------------- |
| Loki overload     | túl sok log     |
| invalid label     | hibás label     |
| Loki config limit | ingestion limit |

---

# 7. Pipeline parsing hibák

Ha a pipeline stage hibás, akkor a log feldolgozás nem működik.

## Példa hiba

```
error parsing json
```

## Ellenőrzés

Promtail log:

```bash
docker logs promtail
```

---

# 8. JSON log parsing nem működik

Pipeline stage:

```yaml
- json:
```

Ha a log nem JSON formátumú, akkor parsing hiba lesz.

## Ellenőrzés

Nézd meg a nyers logot:

```bash
docker logs <container>
```

---

# 9. Label nem jelenik meg Loki-ban

## Tünet

Log stream nem tartalmaz labelt.

Példa query:

```
{container="api"}
```

nem ad vissza logot.

## Ellenőrzés

Promtail config:

```yaml
relabel_configs
```

Ellenőrizd a `target_label` mezőket.

---

# 10. Positions file hiba

Promtail a log pozíciókat egy fájlban tárolja.

```yaml
positions:
  filename: /tmp/positions.yaml
```

Ha a fájl törlődik:

* Promtail újraolvassa a logokat
* duplikált logok jelennek meg

## Ellenőrzés

```bash
docker exec -it promtail cat /tmp/positions.yaml
```

---

# 11. Log duplikáció

## Tünet

Ugyanaz a log többször jelenik meg Loki-ban.

## Gyakori okok

| Ok                     | Magyarázat          |
| ---------------------- | ------------------- |
| positions file törlés  | log újra ingest     |
| több promtail instance | duplikált ingestion |

---

# 12. Promtail túl sok CPU-t használ

## Tünet

* magas CPU
* container load

## Ellenőrzés

```bash
docker stats
```

### Gyakori okok

| Ok                | Magyarázat     |
| ----------------- | -------------- |
| túl sok log       | nagy ingest    |
| túl sok regex     | pipeline stage |
| túl sok container | discovery      |

---

# Promtail API ellenőrzés

Promtail rendelkezik egy HTTP endpointtal.

## Health

```
http://localhost:9080/ready
```

## Metrics

```
http://localhost:9080/metrics
```

---

# Gyors diagnosztikai parancsok

## Promtail log

```bash
docker logs promtail
```

## Promtail health

```bash
curl localhost:9080/ready
```

## Loki kapcsolat teszt

```bash
curl http://loki:3100/ready
```

## Docker container lista

```bash
docker ps
```

## Docker log path

```bash
ls /var/lib/docker/containers
```

---

# Gyors ellenőrzési checklist

| Ellenőrzés            | Parancs                      |
| --------------------- | ---------------------------- |
| Promtail fut          | `docker ps`                  |
| Promtail log          | `docker logs promtail`       |
| Loki elérhető         | `curl loki:3100/ready`       |
| Docker socket mount   | `/var/run/docker.sock`       |
| Docker log path mount | `/var/lib/docker/containers` |
| Positions file        | `/tmp/positions.yaml`        |

---

# Ajánlott monitorozás

Promtail működésének figyeléséhez ajánlott:

* **Grafana**
* **Prometheus**
* Promtail metrics dashboard

---

# Összegzés

A Promtail hibák többsége az alábbi területeken jelentkezik:

* Loki kapcsolat
* Docker log elérés
* service discovery
* pipeline parsing
* konfigurációs hibák

A fenti gyors ellenőrzések segítségével a legtöbb probléma **néhány perc alatt diagnosztizálható és javítható**.
