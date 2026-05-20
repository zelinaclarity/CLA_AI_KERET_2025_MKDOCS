# LiteLLM  frissítési leírás


##  Előfeltétel:
- `Kezdő lépések`-ben leírtak kész vannak


------------------------------------------------------------------------

##  LiteLLM migrációs mód bekapcsolása

A LiteLLM-et migrációs konfigurációval kell elindítani, hogy a szükséges adatbázis-módosítások lefussanak.

``` bash
docker compose -f docker-compose.yml -f docker-compose.migrate.yml up -d litellm
```

### Ellenőrzés, hogy a migrációs mód be van-e kapcsolva

Linuxon:
```bash
{% raw %}
docker inspect litellm --format '{{range .Config.Env}}{{println .}}{{end}}' | grep USE_PRISMA_MIGRATE
{% endraw %}

Windows CMD: 
```bash
{% raw %}
docker inspect litellm --format "{{range .Config.Env}}{{println .}}{{end}}" | findstr USE_PRISMA_MIGRATE
{% endraw %}

Ezt kell válaszként visszakapnod: USE_PRISMA_MIGRATE=true

------------------------------------------------------------------------

##  Compose módosítás

Compose fájlban írd át a litellm verzióját, pl.:

``` yaml
litellm:
  image: ghcr.io/berriai/litellm:v1.82.3-stable.patch.2
```  
  
------------------------------------------------------------------------

##  Teljes stack indítás

``` bash
docker compose up -d
```

------------------------------------------------------------------------
##  patchek telepítése

A LiteLLM adatbázisához kell patch-eket futtatni, hogy a szükséges sémák, objektumok és objektum változások telepítve legyenek.

#### RAG-hoz kapcsolodó patch-ek futtatása
``` bash
docker compose -f docker-compose.yml -f docker-compose.patch.yml run --rm rag-db-patch
```

#### LiteLLM-hez kapcsolodó patch-ek futtatása
``` bash
docker compose -f docker-compose.yml -f docker-compose.patch.yml run --rm litellm-db-patch
```

------------------------------------------------------------------------

##  Log ellenőrzés

``` bash
docker compose logs -f litellm
docker compose logs -f litellm-db
```

------------------------------------------------------------------------
##  LiteLLM migrációs mód kikapcsolása

A LiteLLM-et migrációs konfigurációt ki kell kapcsolni:
``` bash
docker compose -f docker-compose.yml -f docker-compose.nomigrate.yml up -d litellm
```

### Ellenőrzés, hogy a migrációs mód ki van-e kapcsolva

Linuxon:
```bash
{% raw %}
docker inspect litellm --format '{{range .Config.Env}}{{println .}}{{end}}' | grep USE_PRISMA_MIGRATE
{% endraw %}

Windows CMD: 
```bash
{% raw %}
docker inspect litellm --format "{{range .Config.Env}}{{println .}}{{end}}" | findstr USE_PRISMA_MIGRATE
{% endraw %}

Ezt kell válaszként visszakapnod: USE_PRISMA_MIGRATE=false


------------------------------------------------------------------------
##  Log ellenőrzés ismételten
``` bash
docker compose logs -f --tail=50 litellm
docker compose logs -f --tail=50 litellm-db
```

------------------------------------------------------------------------

##  Validáció

-   minden konténer `healthy` vagy stabilan futó állapotban van
-   nincs folyamatos restart
-   nincs adatbázis-kapcsolódási hiba
-   nincs schema vagy migration error
-   LiteLLM login működik
-   LiteLLMben beállított modellek elérhetők az OpenWebUI-ban
-   LiteLLM válaszol
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

  
###  LiteLLM teszt visszatöltés teszt környezetbe

A restore-t érdemes először külön teszt adatbázisba lefuttatni.

A restore teszt compose alapján a teszt adatbázis konténer:

- konténernév: `litellm-db-test`
- adatbázis: `litellm`
- user: `litellm`

A compose fájl alapján a teszt jelszó: `testpass`.


####  Teszt adatbázis indítása

```bash
cd start_scripts
docker compose -f docker-compose.restore-test.yml up -d
cd ..
```

####   LiteLLM backup visszatöltése teszt adatbázisba

```bash
cd start_scripts
python db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean --container litellm-db-test --password testpass
cd ..
```

####   Restore ellenőrzése SQL-lel a teszt adatbázisban

```bash
docker exec -it litellm-db-test psql -U litellm -d litellm -c "select count(*) from public._prisma_migrations;"
```

Ez az ellenőrzés segít megerősíteni, hogy a LiteLLM adatbázis szerkezete és migrációs állapota sikeresen visszaállt.

####   További javasolt ellenőrzések

Javasolt még ellenőrizni:

- a restore script hiba nélkül lefutott-e,
- a teszt adatbázis elindult-e és stabil állapotban maradt-e,
- a visszatöltött táblák száma reális-e,
- a kulcsfontosságú adatok ténylegesen jelen vannak-e.

Példa további ellenőrző lekérdezésekre:

```bash
docker exec -it litellm-db-test psql -U litellm -d litellm -c "\dt"
```

```bash
docker exec -it litellm-db-test psql -U litellm -d litellm -c "select * from public._prisma_migrations limit 5;"
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
litellm:
  image: ghcr.io/berriai/litellm:v1.81.0-stable
```


####  Indítsd el csak az adatbázisokat

```bash
docker compose up -d litellm-db 
```


####  LiteLLM restore futtatása
A restore-t a mentett dump fájlokból kell visszatölteni.

#####  restore parancs:
```bash
cd start_scripts
python db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean
cd ..
```


####  LiteLLM log ellenőrzés

```bash
docker compose logs -f litellm
```


####  Ellenőrizendő

- nincs folyamatos konténer restart,
- nincs adatbázis-kapcsolódási hiba,
- nincs migration vagy schema error,
- a felület betölt,
- a LiteLLM endpointok válaszolnak,
- a korábbi adatok és beállítások látszanak.
------------------------------------------------------------------------

## Ajánlás

-   karbantartási ablakban futtasd
-   előtte teszteld
-   backup kötelező
