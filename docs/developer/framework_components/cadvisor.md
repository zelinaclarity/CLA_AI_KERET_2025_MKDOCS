# <span style="color:#27AE60;">cAdvisor komponens részletes leírása</span>

> **Forrásfájl:** a `docker-compose.monitoring.yml` `cadvisor` service definíciója alapján.

---

## 🎯 Mi a cAdvisor szerepe?

A **cAdvisor** (Container Advisor) a Docker- és konténerkörnyezetek erőforrásfigyelésére szolgáló komponens.

Míg a **Node Exporter** a hosztgép rendszerállapotát figyeli, addig a **cAdvisor** kifejezetten a **konténerek erőforrás-használatára** fókuszál.

Tipikusan az alábbiakat adja:

- konténerenkénti CPU használat
- memóriafogyasztás
- hálózati forgalom
- fájlrendszer-használat
- konténer lifecycle és erőforrás-statisztikák

Ez a komponens tehát különösen hasznos akkor, ha nemcsak azt akarjuk látni, hogy a host terhelt-e, hanem azt is, **melyik konténer mennyire terheli**.

---

## 🧱 A compose fájlban szereplő service

```yaml
cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  container_name: cadvisor
  restart: unless-stopped
  networks:
    - llmnet
  ports:
    - "8088:8080"
  privileged: true
  devices:
    - /dev/kmsg
  volumes:
    - "/:/rootfs:ro"
    - "/var/run:/var/run:ro"
    - "/sys:/sys:ro"
    - "/var/lib/docker:/var/lib/docker:ro"
    - "/dev/disk:/dev/disk:ro"
    - "/var/run/docker.sock:/var/run/docker.sock:ro"
```

---

## 🔍 Beállítások részletes magyarázata

### <span style="color:#0B84F3;">`image: gcr.io/cadvisor/cadvisor:latest`</span>

A konténer a cAdvisor image-et használja a Google Container Registry-ből.

- `gcr.io/cadvisor/cadvisor` → image forrás
- `latest` → legfrissebb tag

**Előnye:**
- gyors indulás,
- kész monitoring komponens,
- szabványos Prometheus integráció.

**Kockázat:**
- a `latest` változhat, ezért stabilitás szempontjából fix verzió sokszor jobb.

---

### <span style="color:#0B84F3;">`container_name: cadvisor`</span>

Explicit konténernév.

**Miért hasznos?**
- könnyebb azonosíthatóság,
- egyszerűbb log- és hibakezelés,
- Prometheus configban is jól illeszkedik a szolgáltatás nevéhez.

---

### <span style="color:#0B84F3;">`restart: unless-stopped`</span>

Újraindítási szabály.

**Jelentése:**
- hiba esetén újraindul,
- host újraindulás után is elindul,
- kézi leállítás esetén nem indul vissza magától.

Konténer-monitoringnál ez különösen fontos, mert ha a monitorozó komponens áll le, megszakad az adatgyűjtés.

---

### <span style="color:#0B84F3;">`networks: - llmnet`</span>

A cAdvisor is a közös `llmnet` hálózatra csatlakozik.

**Miért kell ez?**
- a Prometheus ezen a hálózaton keresztül scrape-eli,
- név alapú feloldással elérhető a `cadvisor` hostname,
- a monitoring komponensek egységes belső kommunikációban működnek.

---

### <span style="color:#0B84F3;">`ports: - "8088:8080"`</span>

Portkitetés a host felé.

- host oldalon: `8088`
- konténeren belül: `8080`

**Mit jelent?**

A cAdvisor saját webes felülete és metrika endpointja a hoston a `8088` porton keresztül érhető el.

**Miért lehet hasznos?**

- böngészőből ellenőrizhető a működése,
- gyors debug,
- kézi ellenőrzés céljából is elérhető.

A Prometheus config viszont a **belső** címet használja:

```yaml
targets: ["cadvisor:8080"]
```

Tehát:
- belső scrape: `cadvisor:8080`
- külső elérés: host `8088`

---

### <span style="color:#0B84F3;">`privileged: true`</span>

Ez egy erős jogosultsági beállítás.

**Mit csinál?**

A konténert emelt jogosultságokkal indítja, így a host rendszerhez mélyebb hozzáférést kap.

**Miért lehet rá szükség?**

A cAdvisornak részletesen látnia kell:

- cgroup adatokat,
- kernel és rendszerinformációkat,
- konténerek erőforrás-használatát,
- Docker runtime környezetet.

**Biztonsági jelentőség:**  
Ez a beállítás csökkenti a konténer izolációját, ezért csak megbízható komponensnél és indokolt esetben ajánlott.

---

### <span style="color:#0B84F3;">`devices: - /dev/kmsg`</span>

A host `/dev/kmsg` eszközét elérhetővé teszi a konténer számára.

**Mi ez?**  
A kernel message bufferhez kapcsolódó eszköz.

**Miért kellhet?**

Bizonyos rendszer- és kernelinformációkhoz, alacsony szintű állapotadatokhoz szükséges lehet.

**Lényeg:**  
a cAdvisor mélyebb rendszerhozzáférést kap, hogy pontosabb monitoringot tudjon végezni.

---

## 💾 `volumes` részletesen

A cAdvisor sok különböző host útvonalat kap becsatolva, mert több helyről olvas konténer- és rendszerinformációt.

---

### <span style="color:#16A085;">`"/:/rootfs:ro"`</span>

A host teljes root fájlrendszere a konténerben `/rootfs` alatt jelenik meg.

**Szerepe:**
- host szintű filesystem információk olvasása,
- konténerfájl-rétegek és környezet jobb értelmezése.

`ro` miatt csak olvasható.

---

### <span style="color:#16A085;">`"/var/run:/var/run:ro"`</span>

A host runtime socketjei és futás közbeni kommunikációs állományai érhetők el.

**Miért hasznos?**
- a Docker runtime és egyéb rendszerkomponensek állapotának olvasásához,
- környezeti információk kinyeréséhez.

---

### <span style="color:#16A085;">`"/sys:/sys:ro"`</span>

A host `sysfs` csatolása.

**Ez különösen fontos**, mert:
- itt érhetők el sokszor a cgroup és kernelhez kapcsolódó információk,
- erőforráskorlátok, CPU, memória és más alacsony szintű adatok innen származhatnak.

---

### <span style="color:#16A085;">`"/var/lib/docker:/var/lib/docker:ro"`</span>

A Docker saját adatterületének becsatolása.

**Miért kell?**
- konténer metadata,
- storage rétegek,
- image és konténerfájlok értelmezése,
- Docker objektumokkal kapcsolatos információk.

---

### <span style="color:#16A085;">`"/dev/disk:/dev/disk:ro"`</span>

A diszkeszközök információihoz ad hozzáférést.

**Haszna:**
- konténerekhez kapcsolható I/O és storage adatok pontosítása,
- block device szintű információk.

---

### <span style="color:#16A085;">`"/var/run/docker.sock:/var/run/docker.sock:ro"`</span>

A Docker daemon socketje.

**Ez az egyik legfontosabb mount.**

**Mire jó?**

- a cAdvisor információt tud szerezni a futó konténerekről,
- hozzáfér a Docker runtime metaadataihoz,
- azonosítani tudja a konténereket és erőforrásaikat.

**Biztonsági szempont:**  
a Docker sockethez való hozzáférés nagyon erős jogosultságnak számít. Itt ugyan `ro`, de önmagában ez is érzékeny mount.

---

## 📡 Kapcsolat a Prometheusszal

A Prometheus configban ez a célpont szerepel:

```yaml
- job_name: "cadvisor"
  static_configs:
    - targets: ["cadvisor:8080"]
```

Ez azt jelenti, hogy a Prometheus a belső Docker hálózaton a `cadvisor` service `8080` portját scrape-eli.

**A host felől** a szolgáltatás a `8088` porton nézhető meg, de **Prometheus számára** a belső port az érdekes.

---

## 🧠 Milyen metrikákat szolgáltathat?

A cAdvisor jellemzően az alábbi kategóriákban ad adatot:

### <span style="color:#D35400;">Konténer CPU</span>
- CPU usage
- throttling
- usage per core
- rendszer / user idő

### <span style="color:#D35400;">Konténer memória</span>
- RSS
- cache
- working set
- memory limit / usage

### <span style="color:#D35400;">Hálózat</span>
- RX / TX byte
- packet számok
- dropped / errored packetek

### <span style="color:#D35400;">Fájlrendszer / storage</span>
- konténerenkénti filesystem használat
- I/O számlálók
- blokkeszköz adatok

### <span style="color:#D35400;">Konténer életciklus</span>
- futó / induló / újrainduló konténerinformációk
- metadata és azonosítók

---

## 🔗 Helye az egész monitoring architektúrában

A három fő komponens szereposztása így néz ki:

- **Prometheus** → gyűjt, tárol, lekérdez
- **Node Exporter** → host gép metrikák
- **cAdvisor** → konténer metrikák

Ez nagyon jó szétválasztás, mert:

- a host és a konténerszintű nézőpont külön kezelhető,
- könnyebb dashboardot és alertet építeni,
- jobban látszik, hogy egy probléma a gépből vagy egy konkrét konténerből ered.

---

## ✅ Összegzés

A cAdvisor ebben a compose fájlban a **Docker konténerek részletes erőforrás-monitorozásáért** felel.

### Fő funkciói:
- konténerszintű metrikák gyűjtése,
- Prometheus számára scrape endpoint biztosítása,
- webes felület publikálása,
- mély host és Docker hozzáférés a pontos metrikákhoz.

### Legfontosabb beállítások:
- **`ports: 8088:8080`** → külső elérés
- **`privileged: true`** → emelt jogosultság
- **`/sys`, `/var/lib/docker`, `docker.sock` mountok** → konténer- és hostinformációk olvasása
- **`/dev/kmsg`** → kernel szintű hozzáférés egy része

---

## 💡 Üzemeltetési megfigyelés

Ez a konfiguráció erőteljesen arra van hangolva, hogy a cAdvisor:

- pontos képet adjon a konténerek erőforrás-használatáról,
- mély rendszer- és Docker-információkhoz jusson,
- közvetlenül integrálódjon a Prometheusba.

Ennek ára a nagyobb jogosultsági szint és a több érzékeny mount, ezért biztonsági szempontból ez egy tudatosan „mélyre nyúló” monitoring komponens.
