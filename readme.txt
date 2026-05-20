Első futtatásnál létre kell hozni a networkot:
docker network create mkdocs-net

Utána:
docker compose up -d

Host fájlba, lokális elérénél:
127.0.0.1 docs.devaiclarity.hu


Elérés:
http://docs.devaiclarity.hu:8010/