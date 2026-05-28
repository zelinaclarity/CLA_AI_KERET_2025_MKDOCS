# Monitoring

## Cél

A monitoring és logging stack beállítása.

## 🏗️ Komponensek

📊 metrikák (Prometheus)

📜 logok (Loki + Promtail)

📈 vizualizáció (Grafana)

⚙️ infrastruktúra + konténer monitorozás (Node Exporter + cAdvisor)

🚀 alkalmazás szint (Phoenix)



## 🧠 Komponensek szerepe

### 🟣 Grafana
- dashboard és vizualizáció
- metrikák grafikus megjelenítése
- több adatforrás támogatása (pl. Prometheus, Loki)
- riasztások és alerting
- rendszer „nézete” (UI réteg)

### 🟡 Loki
- logok gyűjtése és tárolása
- label-alapú log indexelés
- Prometheus-szerű működés logokra
- hatékony, alacsony erőforrásigény
- logok „adatbázisa”

### 🟠 Promtail
- loggyűjtő agent
- fájlok és konténer logok olvasása
- logok címkézése (labeling)
- logok továbbítása Loki felé
- log pipeline „input réteg”

### 🔵 Phoenix
- alkalmazás backend (üzleti logika)
- HTTP API / web szolgáltatás
- logok generálása (→ Promtail → Loki)
- metrikák exportálása (→ Prometheus)
- a rendszer „termelő” komponense

### 🔴 Prometheus
- metrikák gyűjtése
- tárolás
- lekérdezés (PromQL)
- rendszer „agya”

### 🔵 Node Exporter
- host OS állapot
- CPU, RAM, disk, network

### 🟢 cAdvisor
- Docker konténerek
- erőforrás használat konténerenként

## 🌐 Hálózat

Minden komponens a `llmnet` hálózaton kommunikál.

Ez biztosítja:
- név alapú elérést
- izolált kommunikációt

## Indítás

### Hálózat ellenőrzése

Előtte ellenőrizni kell, hogy létezik-e a hálózat:

```bash
docker network ls
```

### Monitoring indítása

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

## Leállítás

```bash
docker compose -f docker-compose.monitoring.yml down
```

## Ellenőrzés

- Grafana elérhető
- logok megjelennek a riportokban

