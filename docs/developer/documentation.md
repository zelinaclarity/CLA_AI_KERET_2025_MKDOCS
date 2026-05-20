# Dokumentáció fejlesztői útmutató

Ez a dokumentum leírja, hogyan működik a projekt dokumentációs
rendszere, és hogyan tudnak a fejlesztők hozzájárulni a dokumentációhoz.

A dokumentáció **docs-as-code** elven működik, Markdown fájlokból áll,
és Git-ben verziózott. A dokumentáció egy része automatikusan
generálódik a `docker-compose.yml` alapján.

------------------------------------------------------------------------

# Dokumentáció szerkezete

A dokumentáció három fő kategóriára van bontva.

    docs/
      developer/
      ops/
      user/
      _generated/

## Fejlesztői dokumentáció

    docs/developer/

Tartalma:

-   architektúra leírás
-   fejlesztői workflow
-   komponensek működése
-   dokumentációs szabályok

------------------------------------------------------------------------

## Telepítési és üzemeltetési dokumentáció

    docs/ops/

Tartalma:

-   telepítési lépések
-   runbookok
-   monitoring
-   backup / restore
-   hibaelhárítás

------------------------------------------------------------------------

## Felhasználói dokumentáció

    docs/user/

Tartalma:

-   OpenWebUI használat
-   felhasználói útmutatók
-   gyakori kérdések

------------------------------------------------------------------------

## Autogenerált dokumentáció

    docs/_generated/

Ez a könyvtár automatikusan generálódik a `docker-compose.yml` alapján.

Tartalma például:

-   service lista
-   environment változók
-   secrets
-   volume mapping
-   Traefik routing

⚠️ Ezeket a fájlokat **nem szabad kézzel szerkeszteni**, mert
generáláskor felülíródnak.

------------------------------------------------------------------------

# Dokumentáció preview indítása

A dokumentáció lokálisan egy MkDocs szerveren keresztül nézhető meg.

A szerver Docker konténerben fut.

## Indítás

``` bash
docker compose -f docker-compose.yml -f docker-compose.docs.yml up -d docs
```

A dokumentáció ezután elérhető:

    http://localhost:8000

------------------------------------------------------------------------

## Logok megtekintése

``` bash
docker compose -f docker-compose.yml -f docker-compose.docs.yml logs -f docs
```

------------------------------------------------------------------------

## Leállítás

``` bash
docker compose -f docker-compose.yml -f docker-compose.docs.yml stop docs
```

------------------------------------------------------------------------

# Autogenerált dokumentáció frissítése

A generált dokumentáció a futó `mkdocs` konténerből futtatható.

## Generálás

``` bash
docker exec -it mkdocs sh -lc "pip -q install pyyaml && python /work/scripts/generate_docs.py"
```

Ez frissíti a következő mappát:

    docs/_generated/

------------------------------------------------------------------------

## Mikor kell generálni?

Ha változik:

-   `docker-compose.yml`
-   service konfiguráció
-   Traefik label
-   environment változó
-   secrets vagy volume mapping

------------------------------------------------------------------------

# Live reload működés

Az MkDocs `serve` mód automatikusan frissíti az oldalt ha változik egy
Markdown fájl.

Windows + Docker Desktop esetén előfordulhat, hogy a fájlfigyelés nem
mindig működik tökéletesen.

Ha a változás nem jelenik meg:

    Ctrl + F5

vagy

``` bash
docker compose -f docker-compose.yml -f docker-compose.docs.yml restart docs
```

------------------------------------------------------------------------

# Dokumentáció szerkesztési szabályok

## Docs-as-code

A dokumentáció a kóddal együtt verziózott.

Minden módosítás Pull Request-en keresztül történjen.

------------------------------------------------------------------------

## Kis fájlok

Ne készítsünk túl nagy dokumentumokat.

Inkább több kisebb oldal:

    architecture/
      overview.md
      auth.md
      logging.md

------------------------------------------------------------------------

## Autogenerált tartalom

A következő mappát **nem szerkesztjük kézzel**:

    docs/_generated/

Ha változtatni kell rajta:

    scripts/generate_docs.py

scriptet kell módosítani.
