# Docling alapú dokumentumfeldolgozás - Fejlesztői dokumentáció

## Áttekintés

A `rag_ingest` komponens strukturált és strukturálatlan dokumentumokat dolgoz fel RAG használatra. A fő cél, hogy a dokumentumokból kereshető szövegchunkok, embeddingek és a dokumentumokban szereplő képekhez tartozó metaadatok készüljenek.

A Docling alapú feldolgozás jelenleg PDF és DOCX fájloknál aktív. Más támogatott szöveges formátumoknál az egyszerűbb `ingest_preprocess.py` alapján történik a szövegkinyerés és chunkolás.

## Fő komponensek

- `ingest.py` - teljes ingest orchestration, státuszkezelés, embedding, vector store feltöltés, kép-chunk összerendelés.
- `docling_processor.py` - Docling parse eredményből chunkok, táblázat-chunkok és chunk metadata előállítása.
- `docling_figures.py` - Docling dokumentumból képek exportja és kép-layout metadata gyűjtése.
- `object_storage.py` - MinIO/S3 kapcsolat és feltöltés.
- `ingest_preprocess.py` - nem Docling alapú fallback szövegkinyerés.
- `check_doc_coverage.py` - ingest coverage és chunk-tartalom ellenőrzés.

## Pipeline

1. Dokumentumok beolvasása a `SOURCE_DIR` könyvtárból.
2. Tartalom hash számítása; változatlan, sikeresen feldolgozott fájlok kihagyása.
3. Vector store azonosító lekérése vagy létrehozása.
4. PDF/DOCX esetén egyszeri Docling konverzió.
5. Ugyanabból a Docling dokumentumobjektumból:
   - képek exportja MinIO-ba,
   - kép metadata előállítása,
   - táblázatok strukturált feldolgozása,
   - chunkolás,
   - chunk metadata előállítása.
6. Kép-chunk proximity matching.
7. Chunkok párhuzamos embeddingelése.
8. Embeddingek streaming batch feltöltése a vector store API-ba.
9. Feldolgozott képek VLM alapú leírátozása és `image_caption` chunkok betöltése.
10. Ingest státusz, hibák és képmetaadatok mentése PostgreSQL-be.

## Memóriakezelés nagy dokumentumoknál

Nagy PDF-eknél a legnagyobb memóriaigényt tipikusan ezek adják:

- a Docling dokumentumobjektum,
- a teljes `chunk_items` lista a szöveges tartalmakkal,
- a kép-export ideiglenes képobjektumai,
- az embedding queue-ban még futó chunkok.

Az ingest dokumentumonként próbálja elengedni ezeket a nagy objektumokat:

- a szöveges embedding fázis után a teljes `chunk_items` lista már nem marad bent a kép-leírátozáshoz,
- a Docling dokumentum referenciája eldobásra kerül,
- a köztes `chunks`, `content`, `figures` változók nullázódnak,
- fut egy explicit `gc.collect()`,
- Linux/glibc környezetben, ha elérhető, `malloc_trim(0)` is lefut.

Ez csökkenti a dokumentumok közötti memóriafelhalmozódást, de nem garantálja, hogy a process RSS minden dokumentum után teljesen visszaáll a kezdeti szintre. Python allocator, natív könyvtárak és a Docling által használt komponensek tarthatnak vissza memóriát.

## Egyszeri Docling parse

PDF/DOCX esetén a dokumentumot csak egyszer konvertáljuk Doclinggel. A korábbi dupla feldolgozás helyett az ingest a `convert_with_docling()` eredményét adja tovább:

- `process_docling_document()` chunkokat és chunk metadata-t készít ugyanabból a Docling dokumentumból.
- `export_figures_from_docling_document()` képeket exportál ugyanabból a Docling dokumentumból.

Ez csökkenti a PDF/DOCX feldolgozási időt, és konzisztenssé teszi a chunkok, táblázatok és képek Docling item sorrendjét.

## Chunk metadata

A chunk metadata alapmezői:

- `doc_id`
- `file_name`
- `source_path`
- `department`
- `chunk_index`
- `chunk_type`
- `section_path`
- `captions`
- `page_numbers`
- `element_labels`
- `has_table`
- `has_figure`
- `content_type`

Docling alapú feldolgozásnál kiegészítő proximity/layout mezők is készülhetnek:

- `doc_item_order_min`
- `doc_item_order_max`
- `doc_item_order_avg`
- `layout_pages`

A `layout_pages` PDF esetén oldalankénti becsült bounding boxot és középkoordinátát tartalmazhat. DOCX esetén ezek nem mindig állnak rendelkezésre, mert a DOCX nem fix oldalkép formátum.

## Táblázatfeldolgozás

A táblázatok nem csak sima folyó szövegként kerülnek be a pipeline-ba. A Docling table elemekből külön strukturált `table_info` készül, majd ebből külön table chunkok generálódnak.

Jelenlegi táblázatkezelés:

- Kis táblázatok egyetlen table chunkként kerülnek be.
- Nagy táblázatok sorcsoportokra vannak bontva.
- Az oszlopfejléc minden table chunkban megismétlődik.
- Az embedding szöveg tartalmazza a tábla azonosítóját, captionjét, section path-ját, oszlopait és a sorokat.
- A metadata tartalmazza a tábla azonosítóját és a sorintervallumot.

Fontos környezeti változók:

- `TABLE_ROW_GROUP_SIZE`
- `TABLE_MAX_ROWS_SINGLE_CHUNK`
- `MAX_EMBED_CHARS`

Table chunk metadata mezői:

- `content_type = "table"`
- `chunk_kind = "table"`
- `table_id`
- `table_index`
- `table_caption`
- `table_columns`
- `table_row_count`
- `table_row_start`
- `table_row_end`
- `table_chunk_index`
- `table_chunk_count`
- `table_doc_item_order`

Vegyes szöveg + tábla chunkoknál a szöveges chunk `content_type = "mixed"` értéket kaphat, miközben a tábla külön table chunkokban is megjelenik.

## Kép export és metadata

A képek exportja MinIO/S3 kompatibilis object storage-ba történik.

Jelenlegi object key minta:

```text
figures/{doc_id}/{uuid}_{figure_id}.png
```

Az exportált képekhez az ingest futás közben az alábbi metadata készülhet:

- `figure_id`
- `figure_index`
- `doc_item_order`
- `page_no`
- `bbox`
- `bbox_center`
- `captions`
- `object_key`
- `bytes`
- `width`
- `height`

A `rag.document_figures` tábla továbbra is a stabil képmetaadatokat tárolja:

```sql
CREATE TABLE IF NOT EXISTS rag.document_figures (
    id bigserial PRIMARY KEY,
    doc_id text NOT NULL,
    file_name text NOT NULL,
    source_path text,
    figure_id text NOT NULL,
    page_no integer,
    caption_text text,
    object_key text NOT NULL,
    bytes integer,
    width integer,
    height integer,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_document_figures_doc_figure
ON rag.document_figures (doc_id, figure_id);
```

A `bbox`, `bbox_center`, `doc_item_order` és `figure_index` jelenleg a futásidejű matchinghez és a chunk metadata gazdagításához használt mezők; ezek nincsenek külön oszlopként mentve a `document_figures` táblába.

## Kép-chunk összerendelés

A kép-chunk összerendelés célja, hogy minden kép az őt körülvevő, legrelevánsabb chunkokhoz kerüljön. A chunk metadata forma mind PDF, mind DOCX esetén azonos:

- `figure_ids`
- `figure_links`
- `related_figure_count`
- `has_related_figures`
- `figure_match_mode`

Példaként egy `figure_links` elem:

```json
{
  "figure_id": "fig_0001",
  "match_types": ["doc_order_before", "layout_proximity"],
  "score": 0.94,
  "proximity_directions": ["before"],
  "page_no": 3,
  "figure_index": 1,
  "figure_doc_item_order": 42,
  "doc_order_distance": 2,
  "layout_distance": 81.4
}
```

### PDF stratégia

PDF esetén a matching elsődlegesen a Docling item sorrendet használja, és ha van layout metadata, akkor page/bbox távolsággal erősíti a kapcsolatot.

Egy képhez legfeljebb két irányú kapcsolat készül:

- a kép előtti legközelebbi chunk,
- a kép utáni legközelebbi chunk.

Ha a kép valamelyik chunk Docling item tartományán belül van, ugyanaz a chunk kaphatja mindkét irányt.

### DOCX stratégia

DOCX esetén a pontos oldal és bounding box kevésbé stabil, ezért a matching elsődlegesen dokumentum olvasási sorrend alapú:

- `doc_order_before`
- `doc_order_after`

Ha Docling mégis ad használható oldal/layout adatot, akkor ugyanaz a metadata forma tud `layout_proximity` jellegű megerősítést is kapni.

### Match mode értékek

- `layout_proximity` - van page/bbox alapú távolsági jel.
- `doc_order_proximity` - dokumentum item sorrend alapú kapcsolat.
- `page_proximity` - csak oldalszám alapú legközelebbi fallback.
- `none` - nincs kapcsolt kép.

## VLM alapú kép-leírátozás

Az ingest opcionálisan a kép export és a fő szöveges ingest után minden feldolgozott képre meghív egy vision-language modellt LiteLLM-en keresztül. A jelenlegi alapmodell:

- `IMAGE_CAPTION_MODEL=qwen2.5-vl-3b-instruct`

A kép a `rag.document_figures.object_key` alapján MinIO/S3-ból kerül visszaolvasásra. A VLM rövid, strukturált leírást készít a kép tartalmáról, majd ebből külön vector chunk készül.

Az `image_caption` chunk metadata fő mezői:

- `content_type = "image_caption"`
- `chunk_type = "image_caption"`
- `figure_caption_source = "vlm"`
- `figure_caption_model`
- `figure_caption_prompt_version`
- `figure_id`
- `figure_ids`
- `object_key`
- `image_type`
- `image_caption_confidence`
- `related_chunk_indexes`
- `page_numbers`
- `section_path`

A VLM futás állapotát a `rag.document_figure_descriptions` tábla tárolja. Ez segít abban, hogy ugyanazzal a `model_name` + `prompt_version` párossal egy sikeresen feldolgozott kép ne fusson újra feleslegesen.

Fontos környezeti változók:

- `IMAGE_CAPTION_ENABLED`
- `IMAGE_CAPTION_MODEL`
- `IMAGE_CAPTION_PROMPT_TEMPLATE_PATH`
- `IMAGE_CAPTION_PROMPT_VERSION`
- `IMAGE_CAPTION_MAX_TOKENS`
- `IMAGE_CAPTION_TEMPERATURE`
- `IMAGE_CAPTION_TIMEOUT`
- `IMAGE_CAPTION_MAX_IMAGE_BYTES`
- `IMAGE_CAPTION_MAX_IMAGE_EDGE`
- `IMAGE_CAPTION_CHUNK_INDEX_BASE`

Az `IMAGE_CAPTION_PROMPT_VERSION` felül tudja írni a template-ben megadott prompt verziót. Ha nincs rá külön szükség, érdemes üresen hagyni, és az aktív prompt saját verzióját használni.

### Prompt template és tesztelés

A VLM promptot az ingest és a teszt ugyanabból a `image_caption_prompt_template.json` fájlból olvassa. A fájlban lehet több prompt is, az ingest az `active` mezőben kijelölt promptot használja.

Az aktív prompt célja nem csak OCR/címkelista, hanem rövid értelmezés is. A Qwen2.5-VL-3B-hez jelenleg az általánosabb `visible_content_v5` prompt az aktív. Ennek várt tartalma:

- egy rövid magyar értelmező mondat,
- fontos látható címkék,
- keresési kulcsszavak.

A `test_image_caption_prompts.py` ugyanazokat az ingest függvényeket hívja, mint a fő pipeline: DB-ből kiválasztja a képeket, MinIO/S3-ból letölti őket, az ingest `describe_image_with_vlm()` függvényével meghívja a modellt, majd az ingest `format_image_caption_text()` kimenetét is kiírja. Nem ír a vector store-ba.

A VLM válaszra quality gate fut. Az ingest nem indexeli a kép-leírást, ha a válasz túl rövid, dekoratív képnek jelöli magát, prompt részleteket mond vissza, erősen ismétlődik, vagy az aktív értelmező promptnál nincs elég látható címke és explicit értelmezés. A teszt script ugyanennek a gate-nek az eredményét is kiírja. A kulcsszavakat az ingest visszaszűri a látható címkékre, hogy a modell ne indexeljen olyan témákat, amelyek nem szerepelnek a képen.

A `SKIP_DECORATIVE` csak akkor jelent automatikus kihagyást, ha a teljes válasz lényegében csak ez az egy jelzés. Ha a modell tévesen `SKIP_DECORATIVE` prefixet ír, de utána ad `Meaning`, `Labels` és `Keywords` tartalmat, az ingest levágja a prefixet és a tartalmat normálisan értékeli.

Ha a modell nem külön `Meaning:` fejléccel kezd, hanem egy rövid bekezdésben ad értelmezést, majd utána következik a `Labels:` és `Keywords:` blokk, az ingest ezt is tudja értelmező válaszként feldolgozni. Ez a Qwen2.5-VL általánosabb válaszstílusa miatt fontos.

Az ingest a kép-caption fázishoz nem tartja meg a teljes eredeti chunklistát. A VLM lépés előtt egy kisebb `figure_context_map` készül, amely csak a szükséges kapcsolatokat viszi tovább:

- `related_chunk_indexes`
- `page_numbers`
- `section_path`
- `figure_links`

Így a kép-caption indexing már nem a teljes dokumentum-szöveget tartja memóriában.

Nagy képek esetén az ingest VLM hívás előtt arányosan lekicsinyíti a képet az `IMAGE_CAPTION_MAX_IMAGE_EDGE` értékre. Ez Qwen2.5-VL jellegű modelleknél segít elkerülni a 2048 tokenes context limit túllépését.

Példa:

```powershell
python .\test_image_caption_prompts.py --file-name "%Data science%" --figure-id fig_0001 --output-dir .\state\image_prompt_tests
```

Összes prompt kipróbálása ugyanabból a template fájlból:

```powershell
python .\test_image_caption_prompts.py --file-name "%Data science%" --limit 0 --all-prompts --output-dir .\state\image_prompt_tests
```

A promptot elég a `image_caption_prompt_template.json` fájlban módosítani; ugyanazt látja az ingest és a teszt is.

## Embedding és vector store feltöltés

Az embedding hívások párhuzamosan futnak. Fontos környezeti változók:

- `EMBEDDING_MODEL`
- `EMBEDDING_DIMENSIONS`
- `EMBEDDING_WORKERS`
- `EMBEDDING_PENDING_LIMIT`
- `MAX_EMBED_CHARS`
- `BATCH_SIZE`

A vector store feltöltés streaming batch működést használ: a teljes dokumentum payloadja nem gyűlik végig memóriában, hanem a kész embeddingek `BATCH_SIZE` méretű csomagokban feltöltődnek.

Az embedding worker-ek egyszerre legfeljebb `EMBEDDING_PENDING_LIMIT` darab chunkot tartanak pending állapotban. Ez fontos védővonal nagy dokumentumoknál, mert a túl nagy pending queue jelentősen növeli a memóriahasználatot.

## Hibakezelés és observability

Az ingest státusz a `rag_ingest_documents` táblában követhető. Az embedding hibák a `rag.rag_ingest_chunk_errors` táblába kerülnek batch insert segítségével.

Tipikus embedding hibák:

- érvénytelen `EMBEDDING_MODEL`,
- rossz `EMBEDDING_DIMENSIONS`,
- LiteLLM jogosultsági hiba,
- rate limit,
- túl hosszú input vagy backend timeout.

## Jelenlegi állapot

- Text pipeline működik.
- Docling PDF/DOCX pipeline működik.
- Kép export működik.
- Kép-chunk proximity matching működik Docling item order alapon.
- PDF esetén layout proximity metadata is használható, ha Docling ad page/bbox adatot.
- DOCX esetén olvasási sorrend alapú proximity matching a stabil alap.
- Táblázatok külön table chunkokban is feldolgozódnak.
- Nagy táblázatok sorcsoportokra vannak bontva.
- VLM alapú kép-leírátozás `image_caption` chunkként bekerülhet a vector store-ba.
- Az ingest és a prompt-teszt ugyanazt a VLM hívási, parser és quality gate logikát használja.
- Multimodális image embedding még nincs.

## Későbbi fejlesztési javaslatok

### Táblázatok

- Külön `markdown_table` és opcionálisan `table_json` tárolása a chunk metadata-ban vagy külön tároló mezőben, hogy retrieval után a válaszgenerátor ne csak plain textet kapjon vissza.
- Táblázat caption és a közvetlenül előtte vagy utána lévő magyarázó bekezdés kapcsolása a table chunk metadata-hoz.
- Sorcsoportosítás finomítása nagyon széles táblázatokra, ahol a `MAX_EMBED_CHARS` miatt oszlopok szerint is törni kellhet.
- Összetett, több soros fejléc vagy merged cellás táblázatok jobb normalizálása.
- Külön `table_match_mode` vagy `table_context_score` metadata, hogy a visszakeresett table chunk mennyire önálló és mennyire igényel környező szöveget.

### Képek

- Külön kapcsolótábla bevezetése kép-chunk relációk auditjához:
  - `doc_id`
  - `chunk_index`
  - `figure_id`
  - `match_type`
  - `score`
  - `page_no`
  - `distance`
- Caption alapú matching hozzáadása a proximity score javításához.
- Gateway oldali külön `image_caption` retrieval lane és kapcsolt képválasztó.
- Image embedding és valódi multimodális kép alapú keresés.

### Retrieval és válaszgenerálás

- Table chunk visszaadásakor a plain text mellett markdown vagy strukturált tábla reprezentáció továbbítása az LLM felé.
- Olyan retriever szabály bevezetése, amely `content_type = "table"` esetén több szomszédos table chunkot együtt ad vissza.
- Vegyes `mixed` chunkoknál a duplikáció mérésen alapuló finomítása, hogy a szöveges és táblázatos reprezentáció ne árassza el a top-k találatokat.

### Minőségbiztosítás

- Mintadokumentum készlet PDF és DOCX formátumokhoz, külön táblafókuszú regressziós ellenőrzésekkel.
- Coverage ellenőrzés bővítése úgy, hogy a táblázatok sorai és oszlopai is külön validálhatók legyenek.
- Futtatás utáni riport a dokumentumonkénti chunk-típus megoszlásról: `text`, `table`, `mixed`.
