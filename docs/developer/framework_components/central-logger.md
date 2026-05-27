# Central Logger komponens összefoglaló

## Áttekintés

A **central-logger** komponens egy központi naplógyűjtő szolgáltatás, amely az infrastruktúra különböző konténereiből érkező logokat fogadja és tárolja. A szolgáltatás **rsyslog alapú syslog szerverként** működik, amely UDP és TCP protokollon keresztül fogad log üzeneteket.

A célja, hogy egységes helyre gyűjtse az összes alkalmazás és szolgáltatás naplóit, így támogatva a hibakeresést, auditot és a monitoring rendszereket.

---

## Technológia

A szolgáltatás az alábbi konténer image-et használja:

```
rsyslog/syslog_appliance_alpine:8.36.0-3.7
```

Ez egy **Alpine Linux alapú rsyslog appliance**, amely kifejezetten centralizált syslog gyűjtésre készült.

---

## Hálózati működés

A central-logger a `llmnet` Docker hálózaton fut, és az alábbi portokon fogad syslog üzeneteket:

| Port | Protokoll | Funkció                            |
| ---- | --------- | ---------------------------------- |
| 5514 | UDP       | gyors, connectionless syslog logok |
| 5514 | TCP       | megbízhatóbb syslog továbbítás     |

Host mapping:

```
5514:5514/udp
5514:5514/tcp
```

Ez lehetővé teszi, hogy a host rendszer és a Docker konténerek egyaránt tudjanak logot küldeni.

---

## Log gyűjtési architektúra

A stack több konténerben használ **Docker syslog logging drivert**, amely a logokat a central-logger felé továbbítja.

Példa konfiguráció egy szolgáltatásnál:

```yaml
logging:
  driver: syslog
  options:
    syslog-address: "udp://127.0.0.1:5514"
    syslog-format: "rfc3164"
    tag: "service-name"
```

### Fontos paraméterek

| Paraméter      | Jelentés               |
| -------------- | ---------------------- |
| syslog-address | a central logger címe  |
| syslog-format  | log formátum (RFC3164) |
| tag            | szolgáltatás azonosító |

Ennek eredményeként minden log esemény tartalmazza a szolgáltatás nevét.

---

## Konfiguráció

A central-logger konfigurációja külső fájlokon keresztül történik.

### Fő konfiguráció

```
./rsyslog/rsyslog.conf
```

### Kiegészítő konfigurációk

```
./rsyslog/conf.d/
```

Ez lehetővé teszi például:

* külön log routing
* log parsing
* log forwarding más rendszerek felé
* strukturált log feldolgozás

---

## Perzisztens tárolás

A konténer több Docker volume-ot használ a logok és munkafájlok tárolására.

| Volume                | Funkció                |
| --------------------- | ---------------------- |
| central-logger-logs   | syslog log fájlok      |
| central-logger-work   | rsyslog queue / buffer |
| central-logger-config | konfiguráció           |
| central-logger-logs2  | további log storage    |

Ez biztosítja, hogy a logok **konténer újraindítás után is megmaradjanak**.

---

## Időzóna

A szolgáltatás a következő időzónával fut:

```
TZ=Europe/Budapest
```

Ez biztosítja, hogy a log timestamp-ek a helyi idő szerint jelenjenek meg.

---

## Szerepe a teljes architektúrában

A central-logger a platform **központi napló infrastruktúrájának első rétege**.

Funkciói:

* konténer logok fogadása
* logok centralizált tárolása
* log routing más rendszerek felé
* debug és audit támogatása


## Docker Compose fájl

```markdown
  central-logger:
    image: rsyslog/syslog_appliance_alpine:8.36.0-3.7
    container_name: central-logger
    restart: unless-stopped
    environment:
      TZ: "Europe/Budapest"
    ports:
      - "5514:5514/udp"
      - "5514:5514/tcp"
    volumes:
      - ./rsyslog/rsyslog.conf:/etc/rsyslog.conf:ro
      - ./rsyslog/conf.d:/etc/rsyslog.d:ro
      - central-logger-logs:/var/log
      - central-logger-work:/work
      - central-logger-config:/config
      - central-logger-logs2:/logs
    networks:
      - llmnet
```

---

## Előnyök

### Centralizált log kezelés

Minden szolgáltatás logja egy helyen érhető el.

### Egységes formátum

Syslog szabvány (RFC3164) használata.

### Skálázhatóság

Új szolgáltatások egyszerűen integrálhatók a syslog driver használatával.

### Hibatűrés

Queue és buffer mechanizmusok csökkentik az adatvesztést.

---

## Összefoglalás

A **central-logger** egy rsyslog alapú központi loggyűjtő szolgáltatás, amely a Docker környezetben futó komponensek naplóit fogadja és tárolja. A syslog protokoll használatával egységes és skálázható log infrastruktúrát biztosít, amely támogatja a monitoring, hibakeresési és audit folyamatokat.
