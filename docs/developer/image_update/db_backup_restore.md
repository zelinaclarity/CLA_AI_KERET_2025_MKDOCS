# Adatbázis mentés és visszatöltés

## Cél

Ez a leírás azt foglalja össze, hogyan kell az `AI_FRAMEWORK` környezetben:

- adatbázis mentést készíteni,
- szükség esetén MinIO bucket mentést készíteni,
- külön teszt adatbázis konténerekbe visszatölteni,
- majd éles vagy cél környezetbe visszatölteni az adatokat.

A dokumentáció a `start_scripts/db_backup_restore.py` segédscript és a `start_scripts/docker-compose.restore-test.yml` teszt compose fájl használatára épül.

## Érintett adatbázisok

A backup/restore script jelenleg ezeket a profilokat támogatja:

| Profil | Konténer | Adatbázis | Felhasználó |
| --- | --- | --- | --- |
| `openwebui` | `openwebui_db` | `openwebui` | `admin` |
| `litellm` | `litellm-db` | `litellm` | `litellm` |
| `rag` | `rag-db` | `rag` | `rag` |

RAG esetén gyakran a MinIO objektumtároló mentése is szükséges, mert a képek és egyéb assetek ott vannak.

## Előfeltételek

- Docker működik a gépen.
- Az adatbázis konténerek indíthatók.
- A `start_scripts/db_backup_restore.py` script elérhető és futtatható.
- A `start_scripts/docker-compose.restore-test.yml` fájl rendelkezésre áll.
- Van elegendő szabad tárhely a dump fájlokhoz és a MinIO mentésekhez.
- Tudod a forrás adatbázis jelszavakat, vagy a script futtatásakor meg tudod adni őket.

## Ajánlott folyamat

Az ajánlott üzemeltetési sorrend:

1. a forrás adatbázisok mentése,
2. ha kell, a MinIO bucket mentése,
3. restore teszt külön teszt konténerekbe,
4. ellenőrzés,
5. éles vagy cél környezetbe restore,
6. szolgáltatások újraindítása és végellenőrzés.

## Hol futtasd a parancsokat

A példák a `start_scripts` könyvtárból indulnak.

Windows:

```powershell
cd C:\Munka\GIT\CLA_AI_KERET_2025\AI_FRAMEWORK\start_scripts
```

Linux:

```bash
cd /opt/AI_FRAMEWORK/start_scripts
```

Ha másik könyvtárból futtatod a scriptet, akkor a kimeneti mappák (`db_backups`, `minio_backups`) az aktuális munkakönyvtárhoz képest jönnek létre.

## Adatbázis mentés készítése

### Szükséges forrás konténerek indítása

Backup előtt indítsd el legalább azokat az adatbázis konténereket, amelyekből menteni szeretnél.

Windows:

```powershell
cd ..
docker compose up -d openwebui_db litellm-db rag-db
cd start_scripts
```

Linux:

```bash
cd /opt/AI_FRAMEWORK
docker compose up -d openwebui_db litellm-db rag-db
cd start_scripts
```

### Teljes adatbázis mentés

Az összes támogatott adatbázis mentése.

Windows:

```powershell
python db_backup_restore.py backup --which openwebui litellm rag
```

Linux:

```bash
python3 db_backup_restore.py backup --which openwebui litellm rag
```

Ha nem adsz meg `--which` paramétert, a script alapértelmezetten szintén az összes ismert profilt menti.

### Egyetlen adatbázis mentése

Például csak a RAG adatbázis mentése.

Windows:

```powershell
python db_backup_restore.py backup --which rag
```

Linux:

```bash
python3 db_backup_restore.py backup --which rag
```

### Kimenet

A script alapértelmezetten a `db_backups/` mappába írja a dump fájlokat:

- `db_backups/openwebui_YYYY-MM-DD_HHMMSS.dump`
- `db_backups/litellm_YYYY-MM-DD_HHMMSS.dump`
- `db_backups/rag_YYYY-MM-DD_HHMMSS.dump`

### Ellenőrzés

Minden mentés után ellenőrizd:

- a script hiba nélkül lefutott-e,
- a dump fájl fizikailag létrejött-e,
- a fájlméret reális-e,
- a mentés időbélyege megfelel-e az aktuális futásnak.

## MinIO mentés készítése

RAG környezetnél érdemes az objektumtároló bucketet is menteni, különösen akkor, ha dokumentumképek vagy assetek is kellenek a visszaállításhoz.

### Egy konkrét bucket mentése

Példa a `rag-assets` bucket mentésére.

Windows:

```powershell
python db_backup_restore.py minio-backup --bucket rag-assets
```

Linux:

```bash
python3 db_backup_restore.py minio-backup --bucket rag-assets
```

### Több bucket mentése

Windows:

```powershell
python db_backup_restore.py minio-backup --bucket rag-assets --bucket another-bucket
```

Linux:

```bash
python3 db_backup_restore.py minio-backup --bucket rag-assets --bucket another-bucket
```

### Összes bucket mentése

Windows:

```powershell
python db_backup_restore.py minio-backup --all-buckets
```

Linux:

```bash
python3 db_backup_restore.py minio-backup --all-buckets
```

### Kimenet

A script alapértelmezetten a `minio_backups/` mappába ír, egy időbélyeges almappába:

- `minio_backups/minio_YYYY-MM-DD_HHMMSS/`

## Restore teszt külön teszt adatbázisokba

Éles restore előtt javasolt a dumpokat külön teszt adatbázisokba visszatölteni.

### Teszt konténerek indítása

Windows:

```powershell
docker compose -f docker-compose.restore-test.yml up -d
```

Linux:

```bash
docker compose -f docker-compose.restore-test.yml up -d
```

Ez a compose fájl a következő teszt konténereket indítja:

| Profil | Teszt konténer | Port | Felhasználó | Adatbázis | Jelszó |
| --- | --- | --- | --- | --- | --- |
| LiteLLM | `litellm-db-test` | `55432` | `litellm` | `litellm` | `testpass` |
| OpenWebUI | `openwebui-db-test` | `55433` | `admin` | `openwebui` | `testpass` |
| RAG | `rag-db-test` | `55434` | `rag` | `rag` | `testpass` |

### OpenWebUI backup visszatöltése teszt konténerbe

Windows:

```powershell
python db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean --container openwebui-db-test --password testpass
```

Linux:

```bash
python3 db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean --container openwebui-db-test --password testpass
```

### LiteLLM backup visszatöltése teszt konténerbe

Windows:

```powershell
python db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean --container litellm-db-test --password testpass
```

Linux:

```bash
python3 db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean --container litellm-db-test --password testpass
```

### RAG backup visszatöltése teszt konténerbe

Windows:

```powershell
python db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean --container rag-db-test --password testpass
```

Linux:

```bash
python3 db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean --container rag-db-test --password testpass
```

### Mire való a `--clean`

A `--clean` kapcsoló a restore előtt törli az ütköző objektumokat a cél adatbázisból. Teszt restore-nál ez erősen javasolt, mert így egy korábbi részleges restore vagy maradványadat nem zavarja meg az eredményt.

### Teszt restore ellenőrzése

Ellenőrizd legalább az alábbiakat:

- a restore script hiba nélkül lefutott-e,
- a teszt konténerek futnak-e,
- a táblák és rekordok megjelentek-e a cél adatbázisban,
- a RAG adatbázisban a várt ingest és metadata rekordok látszanak-e.

### Teszt konténerek leállítása

Ha a teszt restore ellenőrzése kész.

Windows:

```powershell
docker compose -f docker-compose.restore-test.yml down -v
```

Linux:

```bash
docker compose -f docker-compose.restore-test.yml down -v
```

Ez törli a teszt konténerekhez tartozó volume-okat is.

## Éles vagy cél környezetbe visszatöltés

### Ajánlott előkészítés

Restore előtt célszerű:

- alkalmazás oldalon leállítani vagy korlátozni az írást,
- elindítani a cél adatbázis konténereket,
- meggyőződni róla, hogy a megfelelő dump fájlt fogod használni.

### Cél adatbázis konténerek indítása

Windows:

```powershell
cd ..
docker compose up -d openwebui_db litellm-db rag-db minio
cd start_scripts
```

Linux:

```bash
cd /opt/AI_FRAMEWORK
docker compose up -d openwebui_db litellm-db rag-db minio
cd start_scripts
```

### OpenWebUI restore

Windows:

```powershell
python db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean
```

Linux:

```bash
python3 db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean
```

### LiteLLM restore

Windows:

```powershell
python db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean
```

Linux:

```bash
python3 db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean
```

### RAG restore

Windows:

```powershell
python db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean
```

Linux:

```bash
python3 db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean
```

Ha a script nem kap `--password` paramétert, interaktívan bekéri a jelszót.

## MinIO restore

Ha a RAG-hoz szükséges objektumtároló tartalmat is vissza kell állítani, használd a MinIO restore-t is.

### Egy konkrét bucket visszatöltése

Windows:

```powershell
python db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets
```

Linux:

```bash
python3 db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets
```

### Több bucket visszatöltése

Windows:

```powershell
python db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets --bucket another-bucket
```

Linux:

```bash
python3 db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets --bucket another-bucket
```

### Restore szinkron törléssel

Ha azt is szeretnéd, hogy a cél bucketből törlődjenek azok az objektumok, amelyek már nincsenek benne a backupban:

Windows:

```powershell
python db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets --remove
```

Linux:

```bash
python3 db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets --remove
```

Ezt óvatosan használd, mert destruktív lehet.

## RAG környezet visszaállítási sorrend

Ha teljes RAG állapotot akarsz visszaállítani, az ajánlott sorrend:

1. `rag` adatbázis restore,
2. MinIO bucket restore,
3. szükség esetén RAG patch ellenőrzés,
4. `rag-ingest` vagy `rag-gateway` indulás előtti ellenőrzések.

Ennek oka, hogy a RAG adatbázis és a MinIO tartalom együtt ad teljes állapotot a figure rekordokhoz és assetekhez.

## Példa teljes folyamat

### 1. Mentés

Windows:

```powershell
cd C:\Munka\GIT\CLA_AI_KERET_2025\AI_FRAMEWORK
docker compose up -d openwebui_db litellm-db rag-db minio
cd start_scripts
python db_backup_restore.py backup --which openwebui litellm rag
python db_backup_restore.py minio-backup --bucket rag-assets
```

Linux:

```bash
cd /opt/AI_FRAMEWORK
docker compose up -d openwebui_db litellm-db rag-db minio
cd start_scripts
python3 db_backup_restore.py backup --which openwebui litellm rag
python3 db_backup_restore.py minio-backup --bucket rag-assets
```

### 2. Restore teszt

Windows:

```powershell
docker compose -f docker-compose.restore-test.yml up -d
python db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean --container openwebui-db-test --password testpass
python db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean --container litellm-db-test --password testpass
python db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean --container rag-db-test --password testpass
docker compose -f docker-compose.restore-test.yml down -v
```

Linux:

```bash
docker compose -f docker-compose.restore-test.yml up -d
python3 db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean --container openwebui-db-test --password testpass
python3 db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean --container litellm-db-test --password testpass
python3 db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean --container rag-db-test --password testpass
docker compose -f docker-compose.restore-test.yml down -v
```

### 3. Visszatöltés cél környezetbe

Windows:

```powershell
python db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean
python db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean
python db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean
python db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets
```

Linux:

```bash
python3 db_backup_restore.py restore --which openwebui --file db_backups/openwebui_2026-04-15_084518.dump --clean
python3 db_backup_restore.py restore --which litellm --file db_backups/litellm_2026-04-15_084519.dump --clean
python3 db_backup_restore.py restore --which rag --file db_backups/rag_2026-04-15_084520.dump --clean
python3 db_backup_restore.py minio-restore --dir minio_backups/minio_2026-04-15_084530 --bucket rag-assets
```

## Fontos megjegyzések

- Backup nélkül ne indíts restore vagy frissítési folyamatot.
- Teszt restore erősen ajánlott minden jelentős frissítés előtt.
- A `--clean` hasznos, de destruktív: csak akkor használd, ha biztosan a megfelelő cél adatbázisra futtatod.
- A RAG restore önmagában nem mindig elég, ha a MinIO bucket tartalma is része az üzemi állapotnak.
- A script konténernév felülírást is tud, így ugyanazzal a logikával teszt és éles környezet is kezelhető.
- Linux szerveren általában `python3` a helyes parancs; ha van virtuális környezet vagy alias, ehhez igazodj.
