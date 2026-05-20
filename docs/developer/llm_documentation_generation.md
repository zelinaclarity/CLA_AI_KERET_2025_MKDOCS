# LLM dokumentáció generálás

Ez az oldal leírja, hogyan használjuk az LLM-et (ChatGPT / OpenWebUI
stb.) dokumentáció generálására a projektben.

A cél az, hogy minden fejlesztő **ugyanazzal a system prompttal**
dolgozzon, így a generált dokumentáció:

-   egységes szerkezetű
-   MkDocs kompatibilis
-   technikailag pontos
-   nem tartalmaz secret értékeket

A system prompt külön fájlban található, hogy a formázás mindig
megmaradjon.

------------------------------------------------------------------------

# System Prompt fájl

A projektben a system prompt külön fájlban található.

Ajánlott hely a repository-ban:

docs/prompts/llm_docs_system_prompt.txt

A fájl célja:

-   egységes dokumentáció generálás
-   az LLM viselkedésének standardizálása
-   hibás dokumentáció csökkentése

------------------------------------------------------------------------

# Használat

Nyisd meg a system prompt fájlt a repository-ban.

**System prompt fájl (letöltés / megnyitás):**
[llm_docs_system_prompt.txt](../prompts/llm_docs_system_prompt.txt)

2.  Másold ki a teljes tartalmát.

3.  Illeszd be **System Prompt** mezőbe az LLM felületén.

4.  Add meg az input információkat:

-   fejlesztési jegyzetek
-   compose snippet
-   konfiguráció
-   log részletek
-   célközönség (developer / ops / user)

------------------------------------------------------------------------

# Ajánlott input példa

Az LLM-nek adott input lehet például:

Audience: developer

Changes: - new service added - new env variables - compose changes

Config snippet: `<docker compose részlet>`{=html}

Notes: `<fejlesztői jegyzetek>`{=html}

------------------------------------------------------------------------

# Fontos szabály

Az LLM által generált dokumentáció **mindig draft**.

Push előtt kötelező:

-   ellenőrizni a pontosságot
-   ellenőrizni a parancsokat
-   megnézni MkDocs preview-ban
-   frissíteni a nav-ot ha új oldal készült
