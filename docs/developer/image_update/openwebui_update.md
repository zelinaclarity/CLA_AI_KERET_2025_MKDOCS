# Open WebUI frissítési leírás


## Előfeltétel:
- `Kezdő lépések`-ben leírtak kész vannak



------------------------------------------------------------------------

##  Compose módosítás

Compose fájlban írd át a OpenWebUI verzióját, pl.:

``` yaml
openwebui:
  image: ghcr.io/open-webui/open-webui:v0.8.12
```  
  
------------------------------------------------------------------------

##  Teljes stack indítás

``` bash
docker compose up -d
```

------------------------------------------------------------------------

##  Log ellenőrzés

``` bash
docker compose logs -f openwebui
```


------------------------------------------------------------------------

## Validáció

-   minden konténer `healthy` vagy stabilan futó állapotban van
-   nincs folyamatos restart
-   nincs adatbázis-kapcsolódási hiba
-   nincs schema vagy migration error
-   az Open WebUI elérhető
-   Open WebUI login működik
-   modellek elérhetők az OpenWebUI-ban
-   nincs hiba logban


------------------------------------------------------------------------

##  Visszaállítási javaslat hiba esetén (Rollback)

Ha a frissítés után hiba jelentkezik, az alábbi rollback folyamat javasolt.

###  Előfeltételek

A restore megkezdése előtt javasolt ellenőrizni az alábbiakat:

- a backup fájlok elérhetők a `start_scripts/db_backups/` könyvtárban
- a `start_scripts/db_backup_restore.py` script elérhető és futtatható
- a restore teszt compose fájl rendelkezésre áll
- a szükséges konténerek nevei és jelszavai ismertek
- elegendő tárhely rendelkezésre áll a teszt adatbázishoz is

###  Állítsd le a teljes rendszert

```bash
docker compose down
```

  
###  OpenWebUI teszt visszatöltés teszt környezetbe

A restore-t érdemes először külön teszt adatbázisba lefuttatni.

A restore teszt compose alapján a teszt adatbázis konténer:

- konténernév: `openwebui-db-test`
- adatbázis: `openwebui`
- user: `openwebui`

A compose fájl alapján a teszt jelszó: `testpass`.


####  Teszt adatbázis indítása

```bash
cd start_scripts
docker compose -f docker-compose.restore-test.yml up -d
cd ..
```

####  OpenWebUI backup visszatöltése teszt adatbázisba

```bash
cd start_scripts
python db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084519.dump --clean --container openwebui-db-test --password testpass
cd ..
```

####  Restore ellenőrzése SQL-lel

```bash
docker exec -it openwebui-db-test psql -U openwebui -d openwebui -c "select count(*) from public._prisma_migrations;"
```

Ez az ellenőrzés segít megerősíteni, hogy a OpenWebUI adatbázis szerkezete és migrációs állapota sikeresen visszaállt.

####  További javasolt ellenőrzések

Javasolt még ellenőrizni:

- a restore script hiba nélkül lefutott-e,
- a teszt adatbázis elindult-e és stabil állapotban maradt-e,
- a visszatöltött táblák száma reális-e,
- a kulcsfontosságú adatok ténylegesen jelen vannak-e.

Példa további ellenőrző lekérdezésekre:

```bash
docker exec -it openwebui-db-test psql -U openwebui -d openwebui -c "\dt"
```

####  Teszt adatbázis leállítása volume törléssel

```bash
cd start_scripts
docker compose -f docker-compose.restore-test.yml down -v
cd ..
```

### Az adatok visszatöltése a rendes használatban lévő adatbázisba 
Ha sikeres volt az adatok visszatöltése a teszt adatbázisba, akkor el lehet kezdeni a rendes használatban lévő adatbázisba az adatok visszatöltését.

####  Állítsd vissza az image tageket a korábbi stabil verziókra

Példa:

```yaml
openwebui:
  image: ghcr.io/open-webui/open-webui:v0.7.2
```

####  Indítsd el csak az adatbázisokat

```bash
docker compose up -d openwebui_db
```

####  OpenWebUI Restore futtatása

A restore-t a mentett dump fájlokból kell visszatölteni.

#####  restore parancs:

```bash
cd start_scripts
python db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean
cd ..
```
####  Indítsd el az alkalmazásokat

```bash
docker compose up -d
```

####  Rollback utáni ellenőrzés
A rollback után javasolt az alábbiakat ellenőrizni:

#####  Állapotellenőrzés

```bash
docker compose ps
```

#####  Open WebUI log ellenőrzés

```bash
docker compose logs -f openwebui
```

####  Ellenőrizendő

- nincs folyamatos konténer restart,
- nincs adatbázis-kapcsolódási hiba,
- nincs migration vagy schema error,
- a felület betölt,
- a korábbi adatok és beállítások látszanak.
------------------------------------------------------------------------

## Ajánlás

-   karbantartási ablakban futtasd
-   előtte teszteld
-   backup kötelező
