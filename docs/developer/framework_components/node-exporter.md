# <span style="color:#2E86C1;">Node Exporter komponens részletes leírása</span>

> **Forrásfájl:** a `docker-compose.monitoring.yml` `node-exporter` service definíciója alapján.

---

## 🎯 Mi a Node Exporter szerepe?

A **Node Exporter** a Prometheus ökoszisztéma egyik legismertebb exportere.  
Feladata, hogy a **hoszt operációs rendszerből** gyűjtsön metrikákat, és ezeket Prometheus-kompatibilis formában publikálja.

Egyszerűen fogalmazva:

- nem a Docker konténerek belsejét figyeli elsődlegesen,
- hanem a **teljes gép / host rendszer** állapotáról ad képet.

Tipikusan ilyen adatokat szolgáltat:

- CPU kihasználtság
- memóriahasználat
- swap
- fájlrendszerek
- diszk I/O
- hálózati interfészek
- rendszerterhelés
- uptime
- kernel- és OS-szintű mutatók

---

## 🧱 A compose fájlban szereplő service

```yaml
node-exporter:
  image: prom/node-exporter:latest
  container_name: node-exporter
  restart: unless-stopped
  networks:
    - llmnet
  pid: host
  command:
    - "--path.rootfs=/host"
  volumes:
    - "/:/host:ro,rslave"
```

---

## 🔍 Beállítások részletes magyarázata

### <span style="color:#0B84F3;">`image: prom/node-exporter:latest`</span>

A szolgáltatás a hivatalos Node Exporter image-et használja.

- `prom/node-exporter` → image neve
- `latest` → a legfrissebb tag

**Mire jó?**

- gyors telepítés,
- szabványos Prometheus exporter,
- jól dokumentált és széles körben használt komponens.

**Kockázat:**  
a `latest` idővel változik, ezért stabil környezetben érdemes lehet verziót rögzíteni.

---

### <span style="color:#0B84F3;">`container_name: node-exporter`</span>

A konténer explicit neve.

**Előnyei:**

- könnyebb hibakeresés,
- könnyebb logszűrés,
- Docker hálózaton jól ismert, konzisztens név.

---

### <span style="color:#0B84F3;">`restart: unless-stopped`</span>

Automatikus újraindítási szabály.

**Hatása:**

- hiba esetén újraindul,
- host reboot után újraindul,
- ha kézzel leállítják, nem indul vissza automatikusan.

Monitoring komponensnél ez fontos megbízhatósági beállítás.

---

### <span style="color:#0B84F3;">`networks: - llmnet`</span>

A komponens csatlakozik a közös `llmnet` hálózathoz.

**Ennek szerepe:**

- a Prometheus név alapján eléri a `node-exporter` service-t,
- nem kell IP-címekkel dolgozni,
- rendezett konténerközi kommunikáció valósul meg.

A Prometheus config célpontja ehhez illeszkedik: `node-exporter:9100`.

---

### <span style="color:#0B84F3;">`pid: host`</span>

Ez az egyik legfontosabb beállítás ennél a komponensnél.

**Mit csinál?**  
A konténer a hoszt PID namespace-ét használja.

**Miért érdekes ez?**

- jobb rálátást ad a host folyamataira és rendszerállapotára,
- közelebb hozza a konténert a valódi hosztkörnyezethez,
- segít abban, hogy a gyűjtött metrikák valóban a hostot tükrözzék.

**Mit jelent működési szempontból?**

A node-exporter nem elszigetelt konténerként „csak önmagát” látja, hanem a hoszt nézőpontjához közelebb működik.

**Megjegyzés:**  
ez erősebb jogosultsági és izolációs következményekkel jár, ezért csak indokolt esetben használjuk.

---

## ⚙️ `command` részlet

### <span style="color:#8E44AD;">`--path.rootfs=/host`</span>

Ez mondja meg a Node Exporternek, hogy a hoszt root filesystemjét a konténeren belül a `/host` útvonal alatt keresse.

**Miért szükséges?**

Mert a volume mounttal a host `/` könyvtára be van csatolva a konténerbe `/host` alá.

**Enélkül:**

- a node-exporter könnyen a konténer saját fájlrendszerét látná,
- nem a valódi host rendszerből olvasna metrikát.

**Ezzel:**

- a host fájlrendszerére mutat,
- így a metrikák host-szintűek maradnak.

---

## 💾 `volumes` részletesen

### <span style="color:#16A085;">`"/:/host:ro,rslave"`</span>

A teljes host root fájlrendszert becsatolja a konténerbe.

#### Bontás:
- `/` → a host teljes gyökérkönyvtára
- `/host` → a konténeren belüli elérési út
- `ro` → csak olvasható
- `rslave` → mount propagációs beállítás

### Mit jelent a `ro`?

A konténer nem tud írni a host fájlrendszerébe.

**Ez kritikus biztonsági elem**, mert a Node Exporternek alapvetően olvasnia kell, nem módosítania.

### Mit jelent az `rslave`?

Ez egy mount propagation mód.

**Lényege:**  
a hoston megjelenő mount változások a konténer felé tükröződhetnek.

**Miért lehet hasznos?**

Ha új fájlrendszer mountok jelennek meg a hoston, a node-exporter jobban tud korrekt képet adni a filesystem állapotról.

---

## 📡 Milyen porton érhető el?

A compose fájlban nincs külön `ports:` kitétel ehhez a service-hez.

Ez azt jelenti, hogy:

- kívülről közvetlenül nincs publikálva host portra,
- viszont a Docker hálózaton belül a Prometheus eléri.

A csatolt Prometheus config szerint a célpont:

```yaml
targets: ["node-exporter:9100"]
```

Tehát a node-exporter a konténeren belül a szokásos `9100` porton szolgáltat metrikát.

**Ez jó gyakorlat**, mert az exporter nem feltétlenül kell, hogy nyilvánosan kint legyen, ha csak a Prometheus használja.

---

## 🔗 Kapcsolat a Prometheusszal

A Prometheus ezt a service-t így scrape-eli:

```yaml
- job_name: "node-exporter"
  static_configs:
    - targets: ["node-exporter:9100"]
```

**Ez azt jelenti:**

- a Prometheus a `llmnet` hálózaton eléri a `node-exporter` szolgáltatást,
- 15 másodpercenként lekéri a metrikáit,
- ezeket eltárolja saját TSDB-jében.

---

## 🧠 Mit figyel pontosan ez a komponens?

A Node Exporter tipikusan az alábbi kategóriákból szolgáltat adatot:

### <span style="color:#D35400;">CPU</span>
- magonkénti terhelés
- idle / system / user idők
- context switch és interrupt adatok

### <span style="color:#D35400;">Memória</span>
- total / free / available memória
- cache / buffers
- swap használat

### <span style="color:#D35400;">Fájlrendszer</span>
- mountpontonkénti kapacitás
- szabad hely
- inode fogyás
- read-only státusz

### <span style="color:#D35400;">Lemez</span>
- olvasási / írási műveletek
- throughput
- queue és késleltetési mutatók

### <span style="color:#D35400;">Hálózat</span>
- interface forgalom
- dropped packetek
- errorok
- RX / TX byte és packet számlálók

### <span style="color:#D35400;">Rendszerállapot</span>
- uptime
- load average
- kernel információk
- boot time

---

## ✅ Összegzés

A Node Exporter ebben a monitoring stackben a **hosztgép állapotának elsődleges adatforrása**.

### Fő szerepe:
- a host OS metrikáinak begyűjtése,
- Prometheus számára szabványos endpoint biztosítása,
- rendszerterhelés, memória, lemez és hálózat monitorozása.

### A legfontosabb beállítások:
- **`pid: host`** → host process namespace használata
- **`--path.rootfs=/host`** → a host filesystem helyének megadása
- **`/:/host:ro,rslave`** → a host gyökérfájlrendszer becsatolása olvasásra
- **nincs host port publikálás** → csak belső hálózaton érhető el

---

## 💡 Üzemeltetési megfigyelés

Ez a konfiguráció kifejezetten arra van optimalizálva, hogy a Node Exporter:

- **a hostról gyűjtsön valós adatokat**,
- ne csak a konténer izolált környezetét lássa,
- mégis alapvetően csak olvasási hozzáférést kapjon.

Ez egy tipikus és jó Prometheus-os host monitoring minta.
