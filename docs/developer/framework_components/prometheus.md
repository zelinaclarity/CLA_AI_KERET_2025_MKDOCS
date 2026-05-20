# <span style="color:#E6522C;">Prometheus komponens részletes leírása</span>

> **Forrásfájlok:** a `docker-compose.monitoring.yml` Prometheus service definíciója és a csatolt `prometheus.yml` konfiguráció alapján.  
> Ez a dokumentum a szolgáltatás célját, működését és az összes fontos beállítás jelentését részletezi.

---

## 🎯 Mi a Prometheus szerepe?

A **Prometheus** ebben a monitoring stackben a **központi metrika-gyűjtő és idősoros adatbázis**.

Feladata:

- összegyűjteni a metrikákat a többi komponensből,
- eltárolni azokat időbélyeggel együtt,
- lekérdezhetővé tenni őket,
- alapot adni dashboardokhoz, riasztásokhoz és kapacitásfigyeléshez.

Ebben a compose állományban a Prometheus **három célpontot** figyel:

1. **saját magát** (`prometheus:9090`)
2. **node-exporter** (`node-exporter:9100`)
3. **cadvisor** (`cadvisor:8080`)

Ez azt jelenti, hogy a teljes monitoring rendszer „agya” a Prometheus.

---

## 🧱 A compose fájlban szereplő Prometheus szolgáltatás

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  restart: unless-stopped
  networks:
    - llmnet
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - prometheus_data:/prometheus
  command:
    - "--config.file=/etc/prometheus/prometheus.yml"
    - "--storage.tsdb.path=/prometheus"
    - "--storage.tsdb.retention.time=15d"
    - "--web.enable-lifecycle"
```

---

## 🔍 Beállítások részletes magyarázata

### <span style="color:#0B84F3;">`image: prom/prometheus:latest`</span>

Ez adja meg, hogy a konténer a **Prometheus hivatalos Docker image-ét** használja.

- `prom/prometheus` → a repository neve
- `latest` → mindig a legfrissebb taggelt verziót húzza le

**Mit jelent gyakorlatban?**

- gyors indulás,
- kevés karbantartás induláskor,
- viszont hosszú távon **nem determinisztikus**, mert a `latest` változhat.

**Üzemeltetési megjegyzés:**  
stabil környezetben gyakran célszerű fix verziót használni, pl. `prom/prometheus:v2.x.x`, hogy egy friss image ne változtassa meg váratlanul a működést.

---

### <span style="color:#0B84F3;">`container_name: prometheus`</span>

A konténer explicit neve.

**Miért hasznos?**

- könnyebb azonosítani `docker ps` listában,
- egyszerűbb logolásnál és hibakeresésnél,
- a hálózaton belül is jól felismerhető név.

---

### <span style="color:#0B84F3;">`restart: unless-stopped`</span>

Újraindítási politika.

**Jelentése:**

- ha a konténer hibával leáll, Docker automatikusan újraindítja,
- rendszerindítás után is elindul,
- kivétel: ha kézzel le lett állítva, akkor nem indul újra automatikusan.

**Miért jó monitoringnál?**

A monitorozó rendszernek folyamatosan futnia kell. Ez a beállítás növeli a rendelkezésre állást.

---

### <span style="color:#0B84F3;">`networks: - llmnet`</span>

A szolgáltatás a `llmnet` nevű Docker hálózatra csatlakozik.

**Mit biztosít ez?**

- a konténerek név alapján elérik egymást,
- például a Prometheus eléri a `node-exporter` és `cadvisor` szolgáltatásokat,
- elkülönített, rendezett kommunikációt ad.

**Fontos:** a compose alapján ez a hálózat **külső hálózat** (`external: true`), tehát azt előre létre kellett hozni.

---

### <span style="color:#0B84F3;">`ports: - "9090:9090"`</span>

Portkitetés.

**Formátum:** `host_port:container_port`

Itt:

- a hoszt gép `9090` portja
- a konténer `9090` portjára irányít

**Eredmény:**  
a Prometheus webes felülete a hosztról elérhető a `9090`-es porton.

**Mire jó a web UI?**

- target ellenőrzés,
- lekérdezések futtatása,
- metrikák böngészése,
- konfiguráció tesztelése.

---

### <span style="color:#0B84F3;">`volumes`</span>

#### 1. `./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro`

Ez egy bind mount, amely a helyi konfigurációs fájlt csatolja be a konténerbe.

- bal oldal: a hoston lévő fájl
- jobb oldal: a konténerbeli célútvonal
- `:ro` → csak olvasható

**Miért fontos?**

- a Prometheus konfiguráció kívül marad a konténeren,
- egyszerűen szerkeszthető,
- konténer újraépítés nélkül módosítható.

**Miért jó a `ro`?**

- a konténer nem tudja véletlenül felülírni a konfigurációt,
- biztonságosabb,
- kiszámíthatóbb működés.

#### 2. `prometheus_data:/prometheus`

Ez egy named volume.

**Feladata:**

- a Prometheus idősoros adatainak tartós tárolása,
- a konténer újraindítása vagy újra létrehozása után is megmaradnak az adatok.

**Ha ez nem lenne:**

- minden újraindításkor elveszne a történeti metrikaadat.

---

## ⚙️ `command` paraméterek részletesen

### <span style="color:#8E44AD;">`--config.file=/etc/prometheus/prometheus.yml`</span>

Megadja, hogy a Prometheus melyik konfigurációs fájlt használja.

**Szerepe:**

- innen tölti be a scrape beállításokat,
- innen tudja, milyen targeteket figyeljen,
- itt vannak a globális időzítések is.

---

### <span style="color:#8E44AD;">`--storage.tsdb.path=/prometheus`</span>

A beépített **TSDB** (time-series database) tárolási útvonalát adja meg.

**Mit tárol itt?**

- minták,
- indexek,
- blokkok,
- WAL (write-ahead log),
- időalapú metrikaadatok.

Ez a path összekapcsolódik a `prometheus_data` volumennel, így az adatok megmaradnak.

---

### <span style="color:#8E44AD;">`--storage.tsdb.retention.time=15d`</span>

Adatmegőrzési idő.

**Jelentése:**
a Prometheus **15 napig** tartja meg a tárolt metrikákat.

**Miért fontos?**

- korlátozza a tárhelyhasználatot,
- meghatározza, meddig lehet visszanézni a trendeket,
- kompromisszum az adattörténet és a diszkhasználat között.

**Gyakorlati hatás:**

- rövid és középtávú trendfigyelésre elég,
- kapacitás- és teljesítményminták követhetők,
- hosszabb historikus elemzéshez általában nagyobb retention vagy külső tárolás kell.

---

### <span style="color:#8E44AD;">`--web.enable-lifecycle`</span>

Bekapcsolja a lifecycle végpontokat.

**Miért hasznos?**

Lehetővé teszi többek között a konfiguráció **újratöltését újraindítás nélkül**.

**Üzemeltetési előny:**

- config módosítás után nem kell feltétlenül a konténert újraindítani,
- kevesebb kiesés,
- gyorsabb változtatáskezelés.

**Megjegyzés:**  
ez kényelmes, de körültekintően kell használni, főleg ha a webes felület széles körben elérhető.

---

## 📄 A csatolt `prometheus.yml` konfiguráció részletes értelmezése

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]
```

---

## 🌍 `global` szekció

### <span style="color:#16A085;">`scrape_interval: 15s`</span>

Meghatározza, hogy a Prometheus milyen gyakran kérjen le metrikákat a célpontoktól.

**Itt:** 15 másodpercenként.

**Hatása:**

- sűrűbb mintavételezés,
- részletesebb grafikonok,
- gyorsabb anomáliaészlelés,
- de több hálózati és tárolási terhelés.

Ez egy jó általános kompromisszum.

---

### <span style="color:#16A085;">`evaluation_interval: 15s`</span>

A szabályok és riasztási feltételek kiértékelésének periódusa.

**Itt:** 15 másodperc.

Jelen fájlban külön alerting vagy recording rule nincs megadva, de ez a beállítás akkor is azt rögzíti, milyen gyakran történjen szabálykiértékelés.

**Miért fontos előre?**

- későbbi riasztások konzisztensen illeszkednek a scrape gyakorisághoz,
- gyorsabb reakcióidő érhető el.

---

## 🧲 `scrape_configs` szekció

Ez mondja meg a Prometheusnak, **mit figyeljen**, milyen néven, és honnan gyűjtse az adatokat.

Minden `job_name` egy logikai gyűjtési feladat.

---

### <span style="color:#D35400;">`job_name: "prometheus"`</span>

A Prometheus saját magát is monitorozza.

#### `static_configs`
Statikusan megadott célpontokat jelent.

#### `targets: ["prometheus:9090"]`
A Prometheus a Docker hálózaton belüli `prometheus` néven, a `9090` porton érhető el.

**Miért hasznos az önmonitorozás?**

- lekérések állapota,
- belső teljesítménymutatók,
- target health,
- TSDB állapot,
- scraping hibák ellenőrzése.

---

### <span style="color:#D35400;">`job_name: "node-exporter"`</span>

Ez a job a hosztgép rendszer-metrikáit gyűjti.

#### `targets: ["node-exporter:9100"]`

A Prometheus a `node-exporter` szolgáltatást a belső hálózaton a `9100` porton kérdezi le.

**Milyen metrikák jöhetnek innen?**

- CPU terhelés,
- memóriahasználat,
- fájlrendszer statisztikák,
- lemez I/O,
- hálózati forgalom,
- load average,
- egyéb OS-szintű mutatók.

---

### <span style="color:#D35400;">`job_name: "cadvisor"`</span>

Ez a job a konténerekhez kapcsolódó metrikákat gyűjti.

#### `targets: ["cadvisor:8080"]`

A `cadvisor` konténer a belső hálózaton a `8080` porton szolgáltat metrikákat.

**Mit ad tipikusan?**

- konténerenkénti CPU használat,
- memóriahasználat,
- hálózati forgalom,
- fájlrendszerhasználat,
- konténer életciklus- és erőforrásadatok.

**Fontos összefüggés:**  
míg a node-exporter a **hosztot**, addig a cAdvisor a **konténereket** figyeli.

---

## 🔗 Kapcsolat a többi komponenssel

A Prometheus ebben az architektúrában:

- a **node-exporter** felől host szintű metrikát gyűjt,
- a **cadvisor** felől konténerszintű metrikát gyűjt,
- saját magát is ellenőrzi.

Ez együtt egy jól elkülönített monitoring felépítést ad:

- **Prometheus** → gyűjt és tárol
- **node-exporter** → hoszt állapot
- **cadvisor** → Docker konténerek állapota

---

## ✅ Összegzés

A Prometheus komponens ebben a stackben a központi adatgyűjtő és metrikatároló szerepet tölti be.

### Fő funkciói:
- metrikák lekérése 15 másodpercenként,
- adatok tárolása tartós volumebe,
- 15 napos retention biztosítása,
- saját és külső targetek figyelése,
- webes felület biztosítása a lekérdezésekhez.

### A legfontosabb beállítások jelentése röviden:
- **image** → melyik Prometheus image induljon
- **ports** → a webfelület kitettsége
- **volumes** → config és adatok tartóssága
- **retention.time** → adatmegőrzési idő
- **scrape_interval** → milyen gyakran gyűjt metrikát
- **scrape_configs** → honnan gyűjt metrikát

---

## 💡 Üzemeltetési megfigyelés

Ez a konfiguráció egy **könnyen átlátható, minimál, de működőképes monitoring alapot** ad:

- kis számú komponens,
- egyszerű statikus targetlista,
- tartós tárolás,
- host + konténer metrikák együtt,
- jól bővíthető később alertmanagerrel, grafanával vagy további exporterekkel.
