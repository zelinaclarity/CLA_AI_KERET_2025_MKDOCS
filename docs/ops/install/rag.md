# RAG stack

## Cél

A RAG ingest és a kapcsolódó komponensek telepítése úgy, hogy a dokumentumok betölthetőek legyenek a vector adatbázisba.

## Lépések

1. Indítsd el a RAG adatbázist:

    ```bash
    docker compose up -d rag-db
    ```

2. Futtasd le a RAG DB patch-eket, hogy a séma, helper függvények és ingest táblázatok létrejöjjenek:

    ```bash
    docker compose -f docker-compose.yml -f docker-compose.patch.yml run --rm rag-db-patch
    ```

3. Ellenőrizd, hogy a szükséges secret fájlok rendelkezésre állnak. (Ha nem akkor a Új secret rögzítése)

    Az ingesthez legalább ezek kellenek:

    - `./secrets/rag_db_password`
    - `./secrets/rag_vector_store_api_key`
    - `./secrets/litellm_pgvector_embed_service_virtual_key`
    - `./secrets/minio_root_password`

    Ha a gatewayt is indítani akarod, ezen felül ezek is kellenek:

    - `./secrets/litellm_rag_gateway_virtual_key`
    - `./secrets/litellm_db_password`

4. Ha ez a környezet Vault alapú secret kezelést használ, indítsd el a `vault-agent` szolgáltatást is.

    A compose fájlban a MinIO, az ingest és a gateway a `/secrets/...` fájlokat a közös `vault-secrets` volume-ból olvassa:

    ```bash
    docker compose up -d vault-agent
    ```

5. Indítsd el a LiteLLM embedding oldalt és a vector store API-t:

    ```bash
    docker compose up -d litellm litellm-pgvector
    ```

6. Indítsd el a MinIO szolgáltatást, mert a figure export ide menti a képeket:

    ```bash
    docker compose up -d minio
    ```

    A MinIO indulásához ebben a compose setupban ezek kellenek:

    - `MINIO_ROOT_USER` környezeti változó
    - `/secrets/minio_root_password` secret fájl
    - `MINIO_DOMAIN`, ha Traefik mögött, domainnel akarod használni

7. Ellenőrizd a `.env` értékeket a RAG ingesthez.

    Az ingesthez legalább az alábbi változóknak kell értelmes értéket kapniuk:
	
    EMBEDDING_MODEL=<embedding-model-name>
    EMBEDDING_DIMENSIONS=<embedding-dimension>

    MINIO_ROOT_USER=<minio-user>
    MINIO_ENDPOINT=http://minio:9000
    MINIO_DOMAIN=minio.<domain>
    RAG_ASSETS_BUCKET=rag-assets

    IMAGE_CAPTION_ENABLED=true
    IMAGE_CAPTION_MODEL=qwen2.5-vl-3b-instruct
    IMAGE_CAPTION_PROMPT_VERSION=
    IMAGE_CAPTION_MAX_TOKENS=450
    IMAGE_CAPTION_TEMPERATURE=0.1
    IMAGE_CAPTION_TIMEOUT=120
    IMAGE_CAPTION_MAX_IMAGE_BYTES=15728640
    IMAGE_CAPTION_CHUNK_INDEX_BASE=900000

8. Az ingest konténerben használt kapcsolódó értékek általában ezek:

    - `VECTOR_API_BASE_URL=http://litellm-pgvector:8000`
    - `VECTOR_STORE_NAME=general`
    - `LITELLM_BASE_URL=http://litellm:4000`
    - `RAG_META_DB_HOST=rag-db`
    - `RAG_META_DB_PORT=5432`
    - `RAG_META_DB_NAME=rag`
    - `RAG_META_DB_USER=rag`
    - `DEPARTMENT=general`
    - `SOURCE_DIR=/rag_source/general`
    - `CHUNKER=llama`
    - `CHUNK_SIZE=500`
    - `CHUNK_OVERLAP=80`
    - `MAX_EMBED_CHARS=4000`

9. Ha image caption indexing is kell, ellenőrizd, hogy a beállított vision modell elérhető LiteLLM-en keresztül.

    A jelenleg használt modell: `qwen2.5-vl-3b-instruct`.

10. Másold a feldolgozandó dokumentumokat a forrás mappába:

    ```bash
    ./rag/rag_source/general
    ```

11. Indítsd el a `rag-ingest` konténert:

    ```bash
    docker compose up -d rag-ingest
    ```

12. Futtasd le az ingestet a konténerben:

    ```bash
    docker compose exec rag-ingest python ingest.py
    ```

13. Ha a gatewayt is használni akarod, az első sikeres ingest után állítsd be a `VECTOR_STORE_ID` értékét.

    Ezt a `rag_ingest_documents.vector_store_id` mezőből vagy a vector store API-ból tudod kiolvasni.

14. A gatewayhez szükséges további kapcsolódó értékek általában ezek:

    - `VECTOR_STORE_ID=<vector-store-id>`
    - `LITELLM_BASE_URL=http://litellm:4000`
    - `VECTOR_API_BASE_URL=http://litellm-pgvector:8000`
    - `RAG_META_DB_HOST=rag-db`
    - `RAG_META_DB_PORT=5432`
    - `RAG_META_DB_NAME=rag`
    - `RAG_META_DB_USER=rag`
    - `MINIO_ROOT_USER=<minio-user>`
    - `MINIO_ENDPOINT=http://minio:9000`
    - `MINIO_DOMAIN=minio.<domain>`
    - `RAG_ASSETS_BUCKET=rag-assets`
    - `RAG_ASSETS_PUBLIC_BASE_URL=https://minio.<domain>`
    - `RAG_ASSETS_SIGNED_URLS=true`

15. Indítsd el a gatewayt:

    ```bash
    docker compose up -d rag-gateway
    ```

## Adatbázis oldali ellenőrzések

Az első ingest futás után érdemes közvetlenül az adatbázisban is ellenőrizni, hogy a dokumentumok, a képleírások és az embeddingek valóban létrejöttek-e.

### Ingest státuszok ellenőrzése

Ez a lekérdezés megmutatja a feldolgozott dokumentumokat, azok státuszát, hash-ét és a kapcsolódó ingest metaadatokat:

```sql
SELECT * FROM rag.rag_ingest_documents
ORDER BY id ASC;
```

### Képleírások ellenőrzése

Ez a lekérdezés azt mutatja meg, hogy a VLM alapú ábra-/kép-leírások bekerültek-e, milyen prompttal és milyen státusszal futottak le:

```sql
SELECT * FROM rag.document_figure_descriptions
ORDER BY id ASC;
```

### Embedding rekordok ellenőrzése

Ez a lekérdezés a vector store oldali embedding rekordokat mutatja, időrendben visszafelé. Ebből látható, hogy valóban bekerültek-e a szöveges és `image_caption` chunkok:

```sql
SELECT * FROM public.embeddings
ORDER BY created_at DESC;
```

## RAG adatok kézi ürítése

Ha tesztelés vagy újraépítés miatt kézzel szeretnéd üríteni a RAG betöltés eredményeit, az alábbi parancsok használhatók.

!!! warning "Destruktív művelet"
    Ezek a parancsok minden korábban betöltött embeddinget, ingest státuszt, hibalistát, figure rekordot és figure description rekordot törölnek.

```sql
TRUNCATE TABLE public.embeddings;
DELETE FROM rag.rag_ingest_documents;
DELETE FROM rag.rag_ingest_chunk_errors;
DELETE FROM rag.document_figures;
DELETE FROM rag.document_figure_descriptions;
```

Utána a dokumentumok újra teljes ingest feldolgozáson mennek végig.

## Ellenőrzés

- A `vault-agent` lefut, és a szükséges `/secrets/...` fájlok valóban megjelennek a közös secret volume-ban.
- A `rag-db-patch` lefut hiba nélkül.
- A `rag-ingest` konténer elindul.
- Az ingest futás után rekordok jelennek meg a `rag_ingest_documents`, `rag.document_figures` és `rag.document_figure_descriptions` táblában.
- A vector store-ban megjelennek a dokumentum chunkok és az `image_caption` chunkok.
- A gateway csak akkor induljon, ha a `VECTOR_STORE_ID` már be van állítva.

## Fontos környezeti változók

Az alábbi táblák a legfontosabb ingest és gateway környezeti változókat foglalják össze rövid magyarázattal és gyakorlati javaslattal.

### Ingest környezeti változók

| Változó | Mit jelent | Javasolt érték / megjegyzés |
| --- | --- | --- |
| `EMBEDDING_MODEL` | Az embedding modell neve, amely a szöveg- és képcaption chunkokhoz embeddinget készít. | Olyan modellt adj meg, amit a LiteLLM valóban kiszolgál. |
| `EMBEDDING_DIMENSIONS` | Az embedding vektor dimenziója. | Egyezzen a használt embedding modell tényleges dimenziójával. |
| `VECTOR_API_BASE_URL` | A vector store API belső címe. | Tipikusan `http://litellm-pgvector:8000`. |
| `VECTOR_STORE_NAME` | A használt vector store logikai neve. | Általában `general`. |
| `LITELLM_BASE_URL` | A LiteLLM belső API címe. | Tipikusan `http://litellm:4000`. |
| `RAG_META_DB_HOST` | A RAG metaadatbázis hosztneve. | Docker compose-ban általában `rag-db`. |
| `RAG_META_DB_PORT` | A metaadatbázis portja. | Tipikusan `5432`. |
| `RAG_META_DB_NAME` | A metaadatbázis neve. | Általában `rag`. |
| `RAG_META_DB_USER` | A metaadatbázis felhasználóneve. | Általában `rag`. |
| `DEPARTMENT` | A dokumentumok logikai csoportja. | Általában `general`, de lehet szervezeti egység vagy domain név is. |
| `SOURCE_DIR` | Az ingest által olvasott forráskönyvtár. | Például `/rag_source/general`. |
| `CHUNKER` | A chunkolási stratégia. | Jelenleg jellemzően `llama`. |
| `CHUNK_SIZE` | A cél chunkméret karakterben vagy a chunkoló által értelmezett egységben. | Jó kiindulás `500`. Nagyobbra csak méréssel érdemes emelni. |
| `CHUNK_OVERLAP` | A chunkok közötti átfedés. | Jó kiindulás `80`. Túl nagy érték felesleges duplikációt okozhat. |
| `MAX_EMBED_CHARS` | Egy embedding kérésbe küldött maximális szöveghossz. | Jó kiindulás `4000`. Ha túl magas, több timeout és több memóriahasználat lehet. |
| `BATCH_SIZE` | Hány embeddingelt rekord menjen egyszerre a vector store feltöltésbe. | Közepes érték ajánlott; túl nagy érték megdobhatja a memóriaigényt. |
| `EMBEDDING_WORKERS` | Párhuzamos embedding worker-ek száma. | CPU és backend kapacitás alapján érdemes állítani, túl magas érték rate limitet vagy torlódást okozhat. |
| `EMBEDDING_PENDING_LIMIT` | Egyszerre pending állapotban tartható chunkok száma. | Nagy dokumentumoknál fontos memóriafék; ne állítsd indokolatlanul magasra. |
| `MINIO_ROOT_USER` | A MinIO hozzáférési felhasználóneve. | A környezetedhez illeszkedő szolgáltatásfiók. |
| `minio_root_password` secret | A MinIO root jelszava, amelyet a konténer fájlból olvas. | Kötelező elem; a compose szerint `/secrets/minio_root_password` néven kell elérhetőnek lennie. |
| `MINIO_ENDPOINT` | A MinIO belső címe. | Tipikusan `http://minio:9000`. |
| `MINIO_DOMAIN` | A böngészőből elérhető MinIO domain. | Például `minio.<domain>`. |
| `RAG_ASSETS_BUCKET` | Az objektumtároló bucket neve. | Általában `rag-assets`. |
| `IMAGE_CAPTION_ENABLED` | Engedélyezi-e a VLM alapú képleírás készítést. | `true` vagy `false`; ha nem kell képes retrieval, kikapcsolható. |
| `IMAGE_CAPTION_MODEL` | A képleíráshoz használt vision-language modell neve. | Jelenlegi ajánlott érték: `qwen2.5-vl-3b-instruct`. |
| `IMAGE_CAPTION_PROMPT_VERSION` | Opcionális felülírás az aktív prompt verziójára. | Ha nem kell felülírás, maradjon üresen. |
| `IMAGE_CAPTION_MAX_TOKENS` | A VLM válasz maximális tokenhossza. | Jó kiindulás `450`. Túl magas érték hajlamosabb hosszú, zajos válaszokra. |
| `IMAGE_CAPTION_TEMPERATURE` | A VLM válasz kreativitása. | Alacsonyan tartsd, például `0.0`-`0.2`. Nem érdemes magasra emelni, mert nő a hallucináció esélye. |
| `IMAGE_CAPTION_TIMEOUT` | A VLM hívás timeoutja másodpercben. | Jó kiindulás `120`, lassabb lokális modellnél lehet több. |
| `IMAGE_CAPTION_MAX_IMAGE_BYTES` | A képfeldolgozásba engedett maximális képméret bájtban. | Jó kiindulás `15728640` körül. |
| `IMAGE_CAPTION_CHUNK_INDEX_BASE` | A képcaption chunkok kezdő indexbázisa. | Jó, ha jól elkülönül a normál chunk indexektől, például `900000`. |

### Gateway környezeti változók

| Változó | Mit jelent | Javasolt érték / megjegyzés |
| --- | --- | --- |
| `VECTOR_STORE_ID` | A gateway által használt konkrét vector store azonosító. | Csak sikeres első ingest után állítsd be. |
| `LITELLM_BASE_URL` | A LiteLLM belső címe. | Tipikusan `http://litellm:4000`. |
| `VECTOR_API_BASE_URL` | A vector store API belső címe. | Tipikusan `http://litellm-pgvector:8000`. |
| `RAG_META_DB_HOST` | A RAG metaadatbázis hosztja. | Docker compose-ban általában `rag-db`. |
| `RAG_META_DB_PORT` | A metaadatbázis portja. | Tipikusan `5432`. |
| `RAG_META_DB_NAME` | A metaadatbázis neve. | Általában `rag`. |
| `RAG_META_DB_USER` | A metaadatbázis felhasználója. | Általában `rag`. |
| `MINIO_ROOT_USER` | A MinIO hozzáférési felhasználóneve. | Ugyanaz legyen, mint amit az ingest használ. |
| `MINIO_ENDPOINT` | A MinIO belső címe. | Tipikusan `http://minio:9000`. |
| `MINIO_DOMAIN` | A kívülről elérhető MinIO domain. | Például `minio.<domain>`. |
| `RAG_ASSETS_BUCKET` | A képek bucket neve. | Ugyanaz legyen, mint ingest oldalon. |
| `RAG_ASSETS_PUBLIC_BASE_URL` | A képek publikus vagy signed URL alapja. | Tipikusan `https://minio.<domain>`. |
| `RAG_ASSETS_SIGNED_URLS` | Signed URL-eket használjon-e a gateway. | Általában `true`, ez a biztonságosabb alapértelmezés. |
