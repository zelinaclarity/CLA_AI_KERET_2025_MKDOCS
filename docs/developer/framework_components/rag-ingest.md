# RAG Ingest

## Cél

A `rag-ingest` az ingest / chunkolás / embedding workflow futtatására szolgáló komponens.

## Compose szerep

- image: `aiclarity.hu:8443/docker-ssl/rag-ingest:py312-lo`
- container_name: `rag-ingest`

## Függőségek

- `litellm`
- `litellm-pgvector`

## Mountok

- `./rag/rag_ingest:/app:rw`
- `./rag/rag_source:/rag_source:rw`
- `./rag/rag_profile:/rag_profile:r`
- `vault-secrets:/secrets:ro`

## Fő konfiguráció

- vector API base URL
- embedding model és dimensions
- source dir
- chunker paraméterek
- meta DB kapcsolódás

## Parancs

- `sleep infinity`

Ez alapján a konténer inkább futtatási / kézi munkavégzési környezetként szolgál.

## Fejlesztői megjegyzések

- Ez várhatóan erősen fejlesztői/operátori használatú komponens.
- Külön le kell írni az ingest folyamat lépéseit.
