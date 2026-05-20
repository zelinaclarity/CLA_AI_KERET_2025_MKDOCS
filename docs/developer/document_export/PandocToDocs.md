# MkDocs DOCX and PDF Export Script – Dokumentáció

## Áttekintés

Ez a script egy MkDocs-alapú dokumentációs projekt tartalmát exportálja **szekciónként** külön DOCX és/vagy PDF fájlokba. A `mkdocs.yml` navigációs struktúrájából (nav) olvassa ki a fejezeteket, összefűzi az egyes szekciókhoz tartozó Markdown fájlokat, majd DOCX-et (Pandoc segítségével) és PDF-et (WeasyPrint segítségével) generál belőlük.

---

## Előfeltételek

### Python-csomagok

```bash
pip install pyyaml
pip install weasyprint
pip install markdown pygments
```

| Csomag | Mire kell |
|---|---|
| `pyyaml` | `mkdocs.yml` beolvasásához (kötelező) |
| `weasyprint` | PDF generáláshoz |
| `markdown` | Markdown → HTML konverzióhoz (PDF pipeline) |
| `pygments` | Szintaxis-kiemelés (kódblokkok PDF-ben) |

### Külső eszköz: Pandoc

A DOCX generáláshoz **Pandoc** szükséges, melyet külön kell telepíteni:

- [https://pandoc.org/installing.html](https://pandoc.org/installing.html)

A script indításkor automatikusan ellenőrzi, hogy elérhető-e a `pandoc` parancs.

### Fájlrendszer

- Léteznie kell egy `mkdocs.yml` konfigurációs fájlnak.
- A `mkdocs.yml`-ben definiált `nav:` szekció szükséges.
- A Markdown forrásfájloknak elérhetőknek kell lenniük (alapértelmezetten a `docs/` mappában).

---

## Működés

### 1. Konfiguráció beolvasása

A script beolvassa a `mkdocs.yml` fájlt, és kinyeri belőle:
- a `nav:` navigációs struktúrát (fejezetek hierarchiája),
- a `docs/` könyvtár elérési útját (ha nincs megadva, a `mkdocs.yml` melletti `docs/` mappa az alapértelmezett).

### 2. Nav struktúra bejárása

A `nav:` első szintjének minden eleme egy-egy **főszekció** lesz, amely egy önálló kimeneti fájlt eredményez. Az alszekciók és oldalak rekurzívan kerülnek feldolgozásra, a hierarchia mélységét a heading-szintek tükrözik.

### 3. Markdown előfeldolgozás

Minden egyes Markdown fájl esetén a script elvégzi az alábbi tisztítási lépéseket:

- **Front-matter eltávolítása** – a `---` közé zárt YAML fejléc kikerül.
- **MkDocs makrók eltávolítása** – `\{\{ ... \}\}` jelölések törlése.
- **Admonition blokkok átalakítása** – az `!!! note "Cím"` stílusú blokkok blockquote-tá (`> **Cím:** ...`) alakulnak, amelyeket a Pandoc és a WeasyPrint is kezelni tud.
- **Relatív képútvonalak abszolúttá alakítása** – a képhivatkozások `file://` URI-vá konvertálódnak, hogy a WeasyPrint is be tudja tölteni őket.
- **Heading-szintek eltolása** – a nav-hierarchiában elfoglalt mélységnek megfelelően a fejlécek szintje automatikusan igazodik (pl. a 2. szinten lévő oldal `# Cím`-je `## Cím`-mé válik).

### 4. Szekció összefűzése

Az adott főszekció összes Markdown fájlja egyetlen nagy Markdown dokumentummá fűződik össze, pandoc-kompatibilis YAML front-matter-rel (`title`, `toc`, `toc-depth`).

### 5. DOCX generálás (Pandoc)

A Pandoc az összefűzött `.md` fájlból DOCX-et generál az alábbi beállításokkal:
- Automatikus tartalomjegyzék (3 szintű mélységig).
- Szintaxis-kiemelés (`tango` stílus).
- Opcionálisan: egyedi Word-sablon (`--reference-doc`).

> **Megjegyzés a sablonról:** A referencia-dokumentumot a Pandockal kell létrehozni (`pandoc -o reference.docx --print-default-data-file reference.docx`), majd annak stílusait kell testreszabni. Saját, egyedi `.docx` közvetlen sablonként való használata formázatlan kimenetet eredményezhet.

### 6. PDF generálás (WeasyPrint)

A PDF-et a WeasyPrint HTML-alapon állítja elő:
- A Markdown → HTML konverzió a `markdown` könyvtárral történik.
- Az oldal A4-es méretű, 2 cm-es margókkal.
- Tartalmaz oldal fejlécet (dokumentumcím) és oldal lábléct (oldalszám / összes oldal).
- Automatikus tartalomjegyzék az oldal elején.
- Szintaxis-kiemelés (`tango` Pygments stílus).
- Törés- és túlcsordulás-védelem kódblokkoknál, táblázatoknál és képeknél.

### 7. Kimeneti fájlok elnevezése

Minden szekció fájljainak neve: `{sorszám:02d}_{slug}.{kiterjesztés}`

Például az `mkdocs.yml`-ben lévő `Telepítési útmutató` nevű 3. szekció esetén:
```
03_Telepitesi_utmutato.md
03_Telepitesi_utmutato.docx
03_Telepitesi_utmutato.pdf
```

---

## Futtatás

### Alapvető futtatás

```bash
python main.py --mkdocs-yml "C:\projektem\mkdocs.yml"
```

### Egyedi kimeneti mappa megadásával

```bash
python main.py --mkdocs-yml "C:\projektem\mkdocs.yml" --output-dir export
```

### Csak DOCX generálás (PDF nélkül)

```bash
python main.py --mkdocs-yml "C:\projektem\mkdocs.yml" --no-pdf
```

### Csak PDF generálás (DOCX nélkül)

```bash
python main.py --mkdocs-yml "C:\projektem\mkdocs.yml" --no-docx
```

### Egyedi Word-sablon használatával

```bash
python main.py --mkdocs-yml "C:\projektem\mkdocs.yml" --reference-doc cc_sablon.docx
```


A cc_sablon.docx-ben a CC-s beállításokat használom, így ezt érdemes használni.

# Pandoc DOCX sablon generálása
 
Ha a DOCX kimenethez egyedi formázást (betűtípus, színek, stílusok) szeretnél használni,
először egy Pandoc-kompatibilis referencia-dokumentumot kell létrehozni.
 
---
 
## 1. Alap sablon legenerálása
 
```bash
pandoc -o reference.docx --print-default-data-file reference.docx
```
 
Ez létrehoz egy `reference.docx` fájlt a munkakönyvtárban, amely tartalmazza az összes
Pandoc által használt beépített stílust (`Heading 1–6`, `Normal`, `Code`, `Table` stb.).
 
---
---

## Paraméterezés

| Paraméter | Alapértelmezett | Leírás |
|---|---|---|
| `--mkdocs-yml` | `mkdocs.yml` | A `mkdocs.yml` konfigurációs fájl elérési útja. |
| `--docs-dir` | `<mkdocs.yml melletti>/docs` | A Markdown forrásfájlok gyökérmappája. Ha nincs megadva, a `mkdocs.yml` melletti `docs/` mappa. |
| `--output-dir` | `export` | A generált fájlok kimeneti mappája. Ha nem létezik, automatikusan létrejön. |
| `--reference-doc` | *(nincs)* | Pandoc DOCX-sablon (`.docx`) elérési útja az egyedi Word-formázáshoz. |
| `--no-pdf` | *(nincs)* | Ha meg van adva, a PDF generálás kihagyásra kerül. |
| `--no-docx` | *(nincs)* | Ha meg van adva, a DOCX generálás kihagyásra kerül. |

---

## Kimenet

A script futás végén összesítőt ír ki:

```
=======================================================
  Kész! 6 fájl generálva → C:\projektem\export
=======================================================
```

A kimeneti mappában minden főszekció esetén megtalálható:
- `NN_szekciocim.md` – az összefűzött Markdown forrás
- `NN_szekciocim.docx` – Word-dokumentum (ha nem lett kihagyva)
- `NN_szekciocim.pdf` – PDF-dokumentum (ha nem lett kihagyva)

---

## Ismert korlátok és megjegyzések

- **Pandoc TOC a DOCX-ben:** A beillesztett tartalomjegyzék egyszerű szöveges; a kattintható Word-mezők frissítéséhez nyissa meg a dokumentumot Wordben, és frissítse a mezőket (`F9` vagy jobb klikk → Mező frissítése).
- **Hiányzó Markdown fájlok:** Ha a `nav:`-ban hivatkozott fájl nem létezik, a script figyelmeztetést ír ki, és az adott oldal helyett egy `[A fájl nem található]` megjegyzést illeszt be.
- **MkDocs bővítmények:** Csak az admonition és makró szintaxis kerül kezelésre; egyéb MkDocs-specifikus bővítmények (pl. `pymdownx`) kimenetei nem feltétlenül renderelnek helyesen.