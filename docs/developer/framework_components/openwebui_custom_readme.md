# Open WebUI – custom.js és custom.css működése és betöltése

Ez a dokumentáció összefoglalja, hogyan működik az `index.html`, a `custom.js`, a `custom.css`, valamint a külső `model-map.json` konfigurációs fájl, és milyen mechanizmusra épül a csempés modellváltás és a UI testreszabás az Open WebUI felületén.

---

## A custom.js működése

A `custom.js` egy **aszinkron önvégrehajtó (async IIFE)** script, amely betöltéskor:

1. Betölti a modell-hozzárendeléseket a `/static/model-map.json` fájlból  
2. Inicializálja a modellváltó logikát  
3. Dinamikusan beszúrja a csempés gombokat a header fölé  

A script indítása:

```javascript
(async function () {
  console.log("Smart model binding + header buttons loaded");
```

Azért `async`, mert a modellkonfiguráció betöltése HTTP kéréssel (`fetch`) történik, ami aszinkron működésű.

---

### Modellek beállítása a model-map.json-ból

A használt modelleket egy `model-map.json` állományból töltjük be. 

A JSON fájl elvárt formátuma:

```json
{
    "Publikus Chat": "openai-gpt4o-mini-chat-public-v1",
    "Ábra készítés": "openai-gpt4o-mini-image-chart-v1",
    "HR szabályzat": "openai-gpt4o-mini-rag-legal-v1",
    "Kép készítés": "openai-gpt4o-mini-image-image-v1",
    "Szövegfordító agent": "openai-gpt4o-mini-agent-translate-v1"
}
```
Modell konvenció:

```
{szolgáltató}-{modell}-{usecase}-{scope}-{verzió}
```
Ez azt jelenti:

| Gomb felirat | Kiválasztott modell azonosítója |
|-----------------------|---------------------------------------|
| Publikus Chat 		| openai-gpt4o-mini-chat-public-v1 		|
| Ábra készítés 		|openai-gpt4o-mini-image-chart-v1 		|
| HR szabályzat 		| openai-gpt4o-mini-rag-legal-v1 		|
| Kép készítés 			| openai-gpt4o-mini-image-image-v1 		|
| Szövegfordító agent 	| openai-gpt4o-mini-agent-translate-v1 	|


#### OpenWebUI beállítások

A `model-map.json`-ban definiált modellek alapján az OpenWebUI-ban létre kell hozni a megfelelő modell-konfigurációkat. Ezt a `Munkaterület → Modellek` menüpontban lehet megtenni, a `New Model` gombra kattintva.

Példa egy modell rögzítésére:

| Mező | Érték |
|------|-------|
| Modell neve | Publikus Chat |
| Modell azonosító | openai-gpt4o-mini-chat-public-v1 |
| Alapmodell | gpt-4o-mini |

> ⚠️ A modell azonosítónak pontosan egyeznie kell a `model-map.json`-ban szereplő értékkel, különben a gombos modellváltás nem fog működni.

A `Kép készítés` modell esetén a fentiek mellett a `Default Features` szekcióban aktiválni kell a `Képgenerálás` opciót is.

---

## Az index.html szerepe

Az `index.html` az alkalmazás belépési pontja. A `custom.js` és `custom.css` injektálása az alábbi módon történik:

```html
<link rel="stylesheet" href="/static/custom.css" crossorigin="use-credentials" />
...
<script src="/static/custom.js?v=1"></script>
```

A `custom.css` a `<head>`-ben kerül betöltésre, a `custom.js` közvetlenül az `</head>` előtt, hogy az alkalmazás egyéb moduljainak betöltése ne blokkálódjon.

A téma (dark/light/oled-dark/her) az `index.html`-be ágyazott inline script alapján töltődik be a `localStorage.theme` értékéből, FOUC (flash of unstyled content) elkerülése érdekében.

---

## Docker volume alapú injektálás

A `docker-compose.yml` konfigurációban a custom fájlokat volume-ként csatoljuk fel:

```yaml
volumes:
  - ./openwebui/style/custom.css:/app/build/static/custom.css
  - ./openwebui/style/custom.js:/app/build/static/custom.js
  - ./openwebui/style/index.html:/app/build/index.html
  - ./openwebui/style/model-map.json:/app/backend/open_webui/static/model-map.json
```

---

### Mit jelent ez technikailag?

| Host fájl 								| Konténeren belüli cél 						|
|-------------------------------------------|-----------------------------------------------|
| custom.css 								| /app/build/static/custom.css 					|
| custom.js 								| /app/build/static/custom.js 					|
| index.html 								| /app/build/index.html 						|
| model-map.json 							| /app/backend/open_webui/static/model-map.json |

## Docker volume alapú injektálás

OpenWebUI verzióváltásnál az `index.html`-re kell figyelni, hogy az új verzió html-je legyen használva és ahhoz legyenek igazítva a `js` és `css` kódok