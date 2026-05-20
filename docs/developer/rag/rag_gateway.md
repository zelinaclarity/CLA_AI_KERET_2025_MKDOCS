# RAG Gateway fejlesztői dokumentáció

## Áttekintés

A `rag-gateway` az OpenWebUI és a LiteLLM között működő OpenAI-kompatibilis köztes réteg. Feladata, hogy a chat kérésekhez dokumentumkontextust keressen a vector store-ban, a találatokat forrásolható RAG kontextussá rendezze, majd a kérést LiteLLM felé továbbítsa.

A gateway jelenleg szabályalapú retrieval-orchestrator. Köztes LLM-et még nem használ, de a `planner.py` külön rétegként már megtartja a helyet egy későbbi kisebb lokális planner vagy context-builder modellnek.

Fő képességek:

- dokumentumlista és dokumentum-scope kezelés,
- scope-aware vector retrieval,
- table-aware chunk bővítés,
- explicit figure lookup,
- VLM alapú `image_caption` chunkok figyelembe vétele,
- óvatos implicit képcsatolás csak vizuális szándéknál,
- signed MinIO URL-es képmegjelenítés OpenWebUI-ban,
- forrásjelölés dokumentummal és közelítő pozícióval.

## Felhasználói műveletek

Ez a fejezet azt foglalja össze, hogy OpenWebUI chatből hogyan tudja a felhasználó irányítani a RAG működést.

### Dokumentumok listázása

A gateway a RAG metaadatbázisból tudja listázni az ingest által sikeresen feldolgozott dokumentumokat.

Használható parancs:

```text
/docs
```

Természetes nyelven is működik:

```text
Milyen dokumentumok érhetőek el?
Listázd ki az elérhető dokumentumokat.
```

Elvárt válasz:

- fájlnév,
- department,
- chunk darabszám, ha ismert,
- utolsó ingest időpont, ha ismert.

### Dokumentum kiválasztása

Ha a felhasználó egy konkrét dokumentummal akar beszélgetni, a `/use-doc` paranccsal lehet dokumentum-scope-ot beállítani.

Példa:

```text
/use-doc PMBOKGuideSeventhEd_ENG.pdf
```

Ezután a következő kérdéseknél a gateway csak ezt a dokumentumot használja forrásként.

Példa:

```text
Milyen projekt fejlesztési megközelítések vannak a PMBOK szerint?
```

A scope a chat historyból számolódik vissza, tehát a gatewaynek nem kell szerveroldali session állapotot tárolnia.

### Dokumentum kiválasztásának megszüntetése

Az aktív dokumentum-scope törlése:

```text
/clear-doc-scope
```

Ezután a gateway ismét az összes elérhető dokumentumban keres.

### Dokumentum megnevezése természetes nyelven

A gateway megpróbálja felismerni a dokumentumemlítést akkor is, ha nem slash commanddal történik.

Példák:

```text
A PMBOK szerint milyen fejlesztési megközelítések vannak?
```

```text
A Data science dokumentumban milyen tanulási folyamat szerepel?
```

Ilyenkor a gateway a kérdés idejére az említett dokumentumra szűkítheti a retrievalt. A rövid dokumentumaliasok is támogatottak, például `PMBOK` vagy `Data science`.

### Normál szöveges kérdés

Sima információkeresésnél a gateway szöveges kontextust gyűjt, majd a modell válaszol.

Példa:

```text
Milyen projekt fejlesztési megközelítések vannak a PMBOK szerint?
```

Elvárt működés:

- a gateway releváns chunkokat keres,
- a modell szövegesen válaszol,
- a válasz végén `Források:` blokk jelenik meg,
- a gateway alapból nem csatol automatikusan képet.

### Ábra vagy kép keresése

Ha a felhasználó explicit ábrát vagy képet kér, a gateway képválaszt is adhat.

Explicit figure hivatkozás:

```text
Mutasd meg a Figure 2-7 Development Approaches ábrát.
```

Tematikus ábrakeresés:

```text
Van a development approaches témához kapcsolódó ábra?
```

Általános vizuális kérdés:

```text
Milyen ábrázolt folyamatok vannak a PMBOK dokumentumban?
```

Működés:

- explicit `Figure X-Y` hivatkozásnál a gateway direkt figure lookupot és rerankot használ,
- a képet signed MinIO URL-lel adja vissza,
- a válaszban Markdown kép és `Megnyitás:` link jelenhet meg,
- ha nincs megfelelő figure metadata vagy URL, a gateway visszaesik normál RAG válaszra.

Fontos szabály: sima szöveges kérdésnél a gateway nem csatol automatikusan képet. Kapcsolódó kép csak akkor jön, ha a kérdésben van vizuális szándék, például `ábra`, `kép`, `diagram`, `figure`, `image`, `ábrázolt`.

### Táblázat keresése

Ha a felhasználó táblázatot kér, a gateway table-aware módon bővíti a találatokat.

Példák:

```text
Mutasd meg a PMBOK kiadások változásait összefoglaló táblázatot.
```

```text
Van releváns táblázat a data science képzésekről?
```

```text
A Big Data minősítésekről adj vissza táblázatos összefoglalót.
```

Működés:

- a gateway figyeli a `table`, `táblázat`, `táblázatot` jellegű szándékot,
- a table chunkokat külön kezeli,
- ugyanazon `table_id` alá tartozó chunkokat bővítheti,
- a promptba `RELEVÁNS TÁBLÁZATOK` blokk kerülhet,
- a válaszban forrásjelölésnek tartalmaznia kell a dokumentumot és a közelítő pozíciót.

### Források értelmezése

A válaszok végén a gateway által adott vagy a modellnek átadott forrástámpontok alapján `Források:` blokk jelenik meg.

Tipikus forma:

```text
Források:
- PMBOKGuideSeventhEd_ENG.pdf | fejezet: "2.3.3 DEVELOPMENT APPROACHES" | oldal: 130
```

Forrásmezők:

- dokumentumnév,
- fejezet vagy `section_path`,
- oldal vagy oldalak,
- tábla ID, ha táblázatból jött,
- ábra ID, ha képcaption vagy figure chunk volt a forrás.

## Fő komponensek

- `app.py` - FastAPI alkalmazás, OpenAI-kompatibilis endpointok, orchestration, LiteLLM proxyzás.
- `intent_router.py` - user intent, slash commandok, dokumentumemlítések, kép/tábla/figure szándék felismerése.
- `planner.py` - szabályalapú retrieval plan; későbbi lokális LLM planner helye.
- `retrieval.py` - vector search, dynamic top-k, query variantok, `image_caption` lane, table expansion, reranking.
- `prompting.py` - RAG system kontextus, direkt figure válasz, kapcsolódó ábra appendix.
- `document_catalog.py` - RAG meta DB dokumentumlista, figure metadata, signed MinIO URL generálás.
- `gateway_types.py` - dokumentum, chunk, intent, retrieval és figure adatstruktúrák.
- `response_utils.py` - OpenAI-kompatibilis direkt chat response.
- `config.py` - secretkezelés, DB DSN-ek, MinIO és RAG asset konfiguráció.

## Chat pipeline

1. OpenWebUI a gateway `/chat/completions` vagy `/v1/chat/completions` endpointját hívja.
2. A gateway beolvassa a payloadot, kitölti a `user` mezőt, és ellenőrzi az allowlistet.
3. A dokumentumkatalógus lekérdezi az `OK` státuszú dokumentumokat.
4. Az `intent_router` kinyeri az utolsó user kérdést és felismeri:
   - dokumentumlista igény,
   - `/use-doc <fájlnév>` scope parancs,
   - `/clear-doc-scope` parancs,
   - dokumentumemlítés, például `PMBOK szerint`,
   - kép/ábra/figure intent,
   - tábla intent,
   - explicit figure hivatkozás, például `Figure 2-7`.
5. Direkt intent esetén a gateway saját választ ad LiteLLM hívás nélkül.
6. Normál chat esetén a `RuleBasedPlanner` retrieval plant készít.
7. A `retrieval.py` vector search-et futtat, majd bővíti a keresést:
   - magyar-angol query variantokkal,
   - scope filterrel,
   - `image_caption` lane-nel,
   - table chunk expansionnel,
   - figure-aware vagy context-aware rerankinggel.
8. A gateway figure metadata-t kér a RAG meta DB-ből, ha a kérdés képet igényel vagy vizuális szándék miatt releváns kép lehet.
9. Explicit figure kérdésnél a gateway direkt képválaszt ad.
10. Egyéb esetben system RAG kontextust épít és továbbítja a kérést LiteLLM felé.
11. Ha kell, a gateway a modellválasz végére determinisztikusan hozzáad egy `Kapcsolódó ábra` blokkot signed URL-lel.

## Dokumentum-scope

A gateway stateless módon kezeli a scope-ot: a beszélgetés előző user üzeneteiből számolja vissza.

Támogatott módok:

- `/docs` - elérhető dokumentumok listázása.
- `/use-doc <fájlnév>` - beszélgetés szűkítése egy dokumentumra.
- `/clear-doc-scope` - scope törlése.
- természetes dokumentumemlítés - például `PMBOK szerint` vagy `Data science dokumentumban`.

A scope a vector search filtereibe is bekerül `doc_id` és `file_name` alapján.

## Retrieval

### Alap keresési beállítások

- `TOP_K`
- `MIN_SCORE`
- `MAX_CONTEXT_CHARS`
- `DYNAMIC_TOPK_FIRST`
- `DYNAMIC_TOPK_MAX`
- `RETURN_METADATA`
- `RAG_DEPARTMENT`

### Dynamic top-k

A gateway először kisebb limittel keres. Ha a találatok gyengébbek vagy nem elég stabilak, nagyobb limittel bővíti a keresést. Ez csökkenti a latencyt, de nehezebb kérdéseknél mégis több kontextust enged be.

### Query variantok

Bizonyos magyar kifejezésekhez a gateway angol query variantot is futtat, mert a dokumentumok egy része angol. Példa:

```text
fejlesztési megközelítések -> development approaches predictive hybrid adaptive project life cycle
```

Ez segít olyan kérdéseknél, ahol a user magyarul kérdez, de a forrásdokumentum angol.

## Image caption retrieval lane

Az ingest oldalon VLM leírások `content_type = image_caption` chunkként is bekerülhetnek a vector store-ba. A gateway ezeket külön is keresi, és metadata alapján kezeli.

Fontos metadata mezők:

- `content_type = "image_caption"`
- `chunk_type = "image_caption"`
- `figure_id`
- `figure_ids`
- `object_key`
- `image_caption_confidence`
- `figure_caption_source`
- `figure_caption_model`
- `related_chunk_indexes`
- `page_numbers`
- `section_path`

A gateway az `image_caption` chunkokat nem egyszerű szövegként kezeli: figyeli a `figure_id` mezőt, le tudja kérni hozzá a `rag.document_figures` rekordot, majd signed MinIO URL-t tud készíteni a képhez.

## Képkezelés

### Explicit figure kérdés

Ha a user konkrét ábrát kér, például:

```text
Mutasd meg a Figure 2-7 Development Approaches ábrát.
```

akkor a gateway:

- felismeri a `Figure 2-7` hivatkozást,
- figure-aware rerankot futtat,
- lekéri a kapcsolódó figure metadata-t,
- direkt OpenAI-kompatibilis választ ad Markdown képpel,
- nem bízza a kép megjelenítését az LLM-re.

### Vizuális szándék

Ha a user képet, ábrát, diagramot vagy ábrázolt folyamatot kér, a gateway engedékenyebben keres kapcsolódó képeket.

Példák:

```text
Van a development approaches témához kapcsolódó ábra?
Milyen ábrázolt folyamatok vannak a PMBOK dokumentumban?
A data science tanulási folyamatról mit mutat a dokumentumban lévő ábra?
```

Ilyenkor a gateway a modellválasz végére saját `Kapcsolódó ábra` blokkot fűzhet.

### Implicit képcsatolás

Sima szöveges kérdésnél a gateway alapból nem csatol képet. Ez szándékos, mert a kép-VLM chunkok könnyen túl sok képet hozhatnak be.

Példa sima szöveges kérdés:

```text
Milyen projekt fejlesztési megközelítések vannak a PMBOK szerint?
```

Elvárt működés:

- szöveges válasz,
- források,
- automatikus kép nélkül.

Kapcsolódó kép csak akkor jön, ha a kérdésben van vizuális szándék, például `ábra`, `kép`, `diagram`, `figure`, `image`, `ábrázolt`.

### Figure kiválasztási szabályok

A gateway figure kiválasztásnál figyelembe veszi:

- vector search score,
- `figure_links` kapcsolat score,
- `image_caption_confidence`,
- query és képcaption tematikus illeszkedése,
- figure cím illeszkedése, például `Figure 2-7. Development Approaches`,
- képméret szűrő implicit módban, hogy apró vagy dekoratív exportok ne jelenjenek meg.

## Signed MinIO URL

A képek nem public bucketből jönnek. A gateway signed URL-t generál a MinIO/S3 objektumra.

Fontos működési elv:

- ingest belső endpointtal ír: `MINIO_ENDPOINT=http://minio:9000`,
- gateway böngészőből elérhető endpointtal ad signed URL-t: `https://${MINIO_DOMAIN}/...?...X-Amz-...`,
- OpenWebUI-ban a képet a felhasználó böngészője tölti be,
- a bucketnek nem kell public read jogosultság.

Fontos env változók:

- `MINIO_ENDPOINT`
- `MINIO_ROOT_USER`
- `MINIO_DOMAIN`
- `MINIO_PUBLIC_BASE_URL`
- `RAG_ASSETS_BUCKET`
- `RAG_ASSETS_PUBLIC_BASE_URL`
- `RAG_ASSETS_SIGNED_URLS`
- `RAG_ASSETS_SIGNED_URL_TTL_SECONDS`

## Táblázatkezelés

A gateway az ingest által előállított table metadata-t használja.

Fontos mezők:

- `content_type = "table"`
- `content_type = "mixed"`
- `table_id`
- `table_caption`
- `table_columns`
- `table_row_start`
- `table_row_end`

Ha a user táblázatot kér, a gateway ugyanazon `table_id` alá tartozó chunkokat bővítheti, hogy az LLM ne csak egy töredéket kapjon.

## Prompt assembly

A modellnek adott system kontextus fő blokkjai:

- `RAG gateway kontextus`
- aktív dokumentum-scope
- válaszadási szabályok
- retrieval paraméterek
- `RELEVÁNS SZÖVEG`
- opcionálisan `RELEVÁNS TÁBLÁZATOK`
- `FORRÁSJELÖLÉSI TÁMPONTOK`

Fontos: a gateway már nem ad nyers kép URL-eket az LLM kontextusába. Ez csökkenti annak esélyét, hogy a modell rossz vagy nem signed linket másoljon a válaszba. A képcsatolást a gateway saját appendix logikája végzi.

## RAG trace es prompt audit

A gateway opcionálisan részletes RAG trace-t tud menteni adatbázisba. Ennek célja, hogy tesztelésnél és hibakeresésnél visszakereshető legyen a teljes döntési lánc:

- milyen user kérdés érkezett,
- milyen dokumentum-scope volt aktív,
- mit döntött a planner,
- milyen chunkokat adott vissza a vector store,
- mely chunkok kerültek ténylegesen a system promptba,
- milyen system prompt ment tovább LiteLLM felé,
- milyen képek és táblák voltak kiválasztva,
- opcionálisan milyen választ adott vissza a modell.

A trace nem része a válaszgenerálásnak, csak observability és regressziós tesztelési célra szolgál.

### Trace céladatbázis

A trace alapértelmezetten a meglévő RAG meta DB kapcsolatot használja, vagyis a `rag-db` konténert és a `rag` adatbázist.

A gateway-ben ez a kapcsolat már létezik:

```yaml
RAG_META_DB_HOST: "rag-db"
RAG_META_DB_PORT: "5432"
RAG_META_DB_NAME: "rag"
RAG_META_DB_USER: "rag"
RAG_META_DB_PASSWORD_FILE: /secrets/rag_db_password
```

A trace célját a `RAG_GATEWAY_TRACE_DB` szabályozza:

```text
RAG_GATEWAY_TRACE_DB=rag -> RAG_META_DB kapcsolat, vagyis rag-db / rag
RAG_GATEWAY_TRACE_DB=ops -> OPS_DB kapcsolat, vagyis litellm-db / litellm
```

A javasolt beállítás:

```env
RAG_GATEWAY_TRACE_DB=rag
```

Így a trace táblák a `rag-db` alatt, az `ops` sémában jönnek létre:

```text
rag database
└── ops schema
    ├── rag_gateway_runs
    └── rag_gateway_run_chunks
```

### Környezeti változók

Javasolt `.env` beállítások:

```env
RAG_GATEWAY_TRACE_ENABLED=true
RAG_GATEWAY_TRACE_DB=rag
RAG_GATEWAY_TRACE_SCHEMA=ops
RAG_GATEWAY_TRACE_FULL_PROMPT=true
RAG_GATEWAY_TRACE_FULL_CHUNK_TEXT=false
RAG_GATEWAY_TRACE_RESPONSE=false
RAG_GATEWAY_TRACE_MAX_CHUNKS=40
RAG_GATEWAY_TRACE_TEXT_PREVIEW_CHARS=1200
```

A `docker-compose.yml` `rag-gateway.environment` blokkjába ezeket explicit át kell adni, mert a Compose `.env` fájl nem kerül automatikusan teljes egészében a konténer környezetébe:

```yaml
RAG_GATEWAY_TRACE_ENABLED: "${RAG_GATEWAY_TRACE_ENABLED:-false}"
RAG_GATEWAY_TRACE_DB: "${RAG_GATEWAY_TRACE_DB:-rag}"
RAG_GATEWAY_TRACE_SCHEMA: "${RAG_GATEWAY_TRACE_SCHEMA:-ops}"
RAG_GATEWAY_TRACE_FULL_PROMPT: "${RAG_GATEWAY_TRACE_FULL_PROMPT:-true}"
RAG_GATEWAY_TRACE_FULL_CHUNK_TEXT: "${RAG_GATEWAY_TRACE_FULL_CHUNK_TEXT:-false}"
RAG_GATEWAY_TRACE_RESPONSE: "${RAG_GATEWAY_TRACE_RESPONSE:-false}"
RAG_GATEWAY_TRACE_MAX_CHUNKS: "${RAG_GATEWAY_TRACE_MAX_CHUNKS:-40}"
RAG_GATEWAY_TRACE_TEXT_PREVIEW_CHARS: "${RAG_GATEWAY_TRACE_TEXT_PREVIEW_CHARS:-1200}"
```

Induláskor a gateway logban ezt kell látni:

```text
RAG_GATEWAY_TRACE: enabled runs_table=ops.rag_gateway_runs chunks_table=ops.rag_gateway_run_chunks db_target=rag full_prompt=yes full_chunk_text=no response_text=no
```

### Trace táblák

A gateway két táblába ír.

A `ops.rag_gateway_runs` egy RAG kérés fő rekordja. Tipikus mezők:

- `trace_id` - egyedi kérésazonosító,
- `created_at` - kérés ideje,
- `user_email`, `user_id`, `conversation_id`,
- `model`,
- `user_query`, `query_hash`,
- `scope_doc_id`, `scope_file_name`,
- `planner_name`,
- `wants_image`, `wants_table`, `figure_refs`,
- `retrieval_settings`,
- `selected_figures`, `selected_tables`,
- `system_prompt`, `system_prompt_hash`,
- `response_text`, `response_hash`,
- `status`, `error_text`, `latency_ms`.

A `ops.rag_gateway_run_chunks` a vector store-ból visszajött és rerankolt chunkokat tárolja. Tipikus mezők:

- `trace_id`,
- `rank`,
- `score`,
- `included_in_prompt`,
- `doc_id`, `file_name`, `chunk_index`,
- `content_type`,
- `section_path`, `page_numbers`,
- `table_id`,
- `figure_id`, `figure_ids`,
- `text_preview`,
- `text_full`,
- `metadata`.

A `metadata` JSONB mezőben a teljes chunk metadata megmarad, ezért később új mezők bevezetésekor sem kell azonnal táblasémát módosítani.

### Mentési pontok a gateway pipeline-ban

A trace az alábbi pontokon ír:

1. Planner után létrejön a `rag_gateway_runs` rekord `started` státusszal.
2. Retrieval és opcionális table expansion után batch insert-tel mentődnek a chunkok.
3. Figure metadata és prompt assembly után a gateway már ismeri a kiválasztott képeket, táblákat és a system promptot.
4. LiteLLM válasz után a run rekord `completed`, `direct_figure_answer` vagy `llm_error` státuszra frissül.

Direkt gateway válasznál, például explicit figure answer esetén, a trace LiteLLM hívás nélkül is lezáródik.

### Teljesítményvédelmek

A trace úgy készült, hogy alapállapotban kicsi legyen a többletterhelése:

- ha `RAG_GATEWAY_TRACE_ENABLED=false`, a trace writer no-op,
- ha nincs DB pool, a trace writer no-op,
- ha az első DB írás hibázik, a trace writer warning után kikapcsolja magát az adott processben,
- a chunkok `executemany` batch insert-tel mentődnek,
- alapból csak `text_preview` kerül mentésre, nem a teljes chunk szöveg,
- alapból a modellválasz szövege nem kerül mentésre,
- streaming válasznál csak akkor gyűjti a response textet, ha `RAG_GATEWAY_TRACE_RESPONSE=true`.

A legfontosabb kapcsolók:

```text
RAG_GATEWAY_TRACE_FULL_PROMPT=true
```

Mentse-e a teljes system promptot. Teszteléshez hasznos, ezért javasolt bekapcsolni.

```text
RAG_GATEWAY_TRACE_FULL_CHUNK_TEXT=false
```

Mentse-e a teljes chunk szöveget. Alapból érdemes kikapcsolva hagyni, mert nagy dokumentumoknál gyorsan sok adatot termel.

```text
RAG_GATEWAY_TRACE_RESPONSE=false
```

Mentse-e az LLM válaszát. Alapból kikapcsolt, mert streaming esetben extra feldolgozást igényel és adatvédelmi szempontból is érzékenyebb lehet.

### Hibakeresési lekérdezések

Legutóbbi RAG kérések:

```sql
SELECT id, trace_id, created_at, model, scope_file_name, status, latency_ms, user_query
FROM ops.rag_gateway_runs
ORDER BY created_at DESC
LIMIT 20;
```

Egy kérés chunkjai:

```sql
SELECT rank, score, included_in_prompt, file_name, chunk_index, content_type, section_path, page_numbers, text_preview
FROM ops.rag_gateway_run_chunks
WHERE trace_id = '<trace_id>'
ORDER BY rank;
```

A ténylegesen kiküldött system prompt:

```sql
SELECT user_query, system_prompt
FROM ops.rag_gateway_runs
WHERE trace_id = '<trace_id>';
```

Képkiválasztás ellenőrzése:

```sql
SELECT trace_id, selected_figures
FROM ops.rag_gateway_runs
WHERE jsonb_array_length(COALESCE(selected_figures, '[]'::jsonb)) > 0
ORDER BY created_at DESC
LIMIT 20;
```

Táblázatos találatok ellenőrzése:

```sql
SELECT trace_id, rank, score, file_name, table_id, text_preview
FROM ops.rag_gateway_run_chunks
WHERE content_type = 'table'
ORDER BY id DESC
LIMIT 50;
```

### Gyakori hibák

Ha a logban ez látszik:

```text
RAG_GATEWAY_TRACE: disabled
```

akkor a konténer nem kapta meg a `RAG_GATEWAY_TRACE_ENABLED=true` változót.

Ha ez látszik:

```text
UndefinedTableError('relation "ops.rag_gateway_runs" does not exist')
```

akkor a trace be van kapcsolva, de a táblák nem abban az adatbázisban vagy sémában vannak, ahová a gateway ír. `RAG_GATEWAY_TRACE_DB=rag` esetén a tábláknak a `rag-db` konténer `rag` adatbázisában kell lenniük.

Ellenőrzés:

```powershell
docker compose exec rag-db psql -U rag -d rag -c "\dt ops.*"
```

A táblák létrehozása vagy env módosítás után a gateway konténert újra kell indítani:

```powershell
docker compose up -d --force-recreate rag-gateway
```

## Endpointok

- `GET /health`
- `GET /models`
- `GET /v1/models`
- `GET /documents`
- `POST /chat/completions`
- `POST /v1/chat/completions`
- `POST /embeddings`
- `POST /v1/embeddings`

Az `embeddings` endpoint nem RAG-ol, csak LiteLLM proxy.

## Hibatűrő működés

- Ha a retrieval elbukik, a gateway kontextus nélkül is továbbítja a kérést LiteLLM felé.
- Ha nincs RAG meta DB, dokumentumlista és képmetadata funkciók korlátozottak.
- Ha nincs figure metadata vagy signed URL, a szöveges válasz továbbra is működhet.
- Ha a modell már tartalmaz kép URL-t vagy Markdown képet, a gateway nem fűz hozzá második képblokkot.

## Jelenlegi állapot

- Dokumentumlista működik.
- Dokumentum-scope működik slash commanddal és dokumentumemlítéssel.
- PMBOK és Data science jellegű rövid dokumentumaliasok felismerhetők.
- Scope-aware retrieval működik.
- Magyar-angol query variantok segítik az angol dokumentumok keresését.
- Table-aware chunk expansion működik.
- Explicit figure lookup működik.
- VLM alapú `image_caption` chunkok külön retrieval lane-t kapnak.
- Signed MinIO képmegjelenítés működik.
- Sima szöveges kérdésnél a gateway nem csatol automatikusan képet.
- Vizuális szándéknál a gateway kapcsolódó ábrát csatolhat, de szigorúbb relevancia- és méretszűrőkkel.

## Tesztkérdések

Sima szöveges RAG:

```text
Milyen projekt fejlesztési megközelítések vannak a PMBOK szerint?
```

Elvárt: szöveges válasz és források, automatikus kép nélkül.

Explicit ábra:

```text
Mutasd meg a Figure 2-7 Development Approaches ábrát.
```

Elvárt: direkt képválasz signed MinIO URL-lel.

Vizuális szándék:

```text
Van a development approaches témához kapcsolódó ábra?
```

Elvárt: szöveges válasz és egy releváns `Kapcsolódó ábra` blokk.

Image caption teszt:

```text
A data science tanulási folyamatról mit mutat a dokumentumban lévő ábra?
```

Elvárt: a VLM képcaption chunk segítségével megtalált válasz és kapcsolódó kép, ha van erős találat.

Tábla teszt:

```text
Mutasd meg a PMBOK kiadások változásait összefoglaló táblázatot.
```

Elvárt: table-aware kontextus és forrásjelölés.

## Későbbi fejlesztési irányok

- Külön `related_image_selector.py` modul a mostani `prompting.py` logika szétválasztására.
- Image caption score kalibráció dokumentumtípusonként.
- Figure caption normalizálás és emberi olvasható cím mentése DB-be.
- Signed URL TTL finomhangolása.
- Lokális LLM planner query rewrite és chunk pruning célra.
- Retrieval debug endpoint a végső chunklista és képjelöltek megtekintéséhez.
