------------------------------------------------------------------------

# Frissítés célja

A frissítés célja az Open WebUI és a LiteLLM komponensek újabb stabil
verzióra emelése, a szükséges adatbázis-mentési és migrációs lépések
elvégzésével, minimális kockázat mellett.

------------------------------------------------------------------------

# Előfeltételek

-   a `develop` branch naprakész
-   szükséges docker compose fájlok elérhetők:
	- `docker-compose.yml`
	- `docker-compose.migrate.yml`
-   a `start_scripts/db_backup_restore.py` script elérhető és futtatható
-   van elegendő szabad tárhely az adatbázis mentéséhez

------------------------------------------------------------------------

# Frissítési lépések

##  Branch létrehozás

Hozz létre egy új branchet a `develop` branch alapján a frissítéshez. A branch neve legyen az aktuális dátum, pl. 20260416 :

``` bash
git checkout develop
git pull
git checkout -b update/20260416
```

------------------------------------------------------------------------



##  DB mentés
A frissítés előtt kötelező adatbázis-mentést készíteni.
####Indítsd el az adatbázis konténereket:

``` bash
docker compose up -d openwebui_db litellm-db
```

####Futtasd a mentést:

``` bash
cd start_scripts
python db_backup_restore.py backup
cd ..
```

####Ellenőrizendő:
- a mentés sikeresen lefutott-e
- a backup fájl fizikailag létrejött-e
- a backup mérete reális-e
