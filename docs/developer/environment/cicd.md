# CI/CD Vault folyamat kialakítása

**Dátum:** 2026.04.14.  
**Verzió:** v1.0  
**Szerző:** Zelina Attila  

---

## Dokumentum kontroll

| Dátum       | Verzió | Szerző        | Megjegyzés                                   |
|------------|--------|---------------|----------------------------------------------|
| 2026.04.14 | 1.0    | Zelina Attila | Első draft verzió                            |


---


##  Virtual environment létrehozása
Ha már létezik, nem kell létrehozni.

```bash
cd /home/ccai01admin/ccaikeret
python3 -m venv venv
```

##  Aktiválás
```bash
source venv/bin/activate
```

##  Flask telepítése a venv-be
```bash
pip install --upgrade pip
pip install flask
```

##  Waitress telepítése a venv-be
```bash
pip install waitress
pip show waitress
```

##  Logrotate config létrehozása
```bash
sudo nano /etc/logrotate.d/mkdocs_webhook
```

Tedd bele ezt:
```bash
/home/ccai01admin/ccaikeret-docs/mkdocs_webhook.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su ccai01admin ccai01admin
}
```

Mit jelent ez:

-	daily → naponta rotál 
-	rotate 7 → 7 napig tartja meg 
-	compress → gzip tömörítés 
-	delaycompress → ne azonnal tömörítsen 
-	missingok → ha nincs log, ne hibázzon 
-	notifempty → ha üres, ne rotáljon 
-	copytruncate → futó service mellett is működik 

##  Ellenőrzés, hogy fut-e
```bash
ps aux | grep mkdocs_webhook.py
```

##  Teszt a böngészőből vagy curl-lal
Ha a Flask listener 9000-es porton fut:
```bash
curl -X POST http://172.28.10.13:9000/payload \
     -H "Content-Type: application/json" \
     -d '{"ref": "refs/heads/develop"}'
```

-	Ez szimulálja a GitHub push eseményt a develop branch-re 
-	Ha minden rendben van, a docker compose parancs lefut a szerveren → a docs konténer újraindul

Tesztelés:
```bash
sudo logrotate -f /etc/logrotate.d/mkdocs_webhook
ls -lh /home/ccai01admin/ccaikeret-docs/
```

Ha nem fut:
```bash
systemctl status logrotate.timer
```

Ellenőrzés:
```bash
sudo systemctl enable logrotate.timer
sudo systemctl start logrotate.timer
```

##  Log olvasás
```bash
tail -f nohup.out
```

##  WebHook létrehozása
Hozzuk létre a mkdocs_webhook.py fájlt, majd másoljuk bele az alábbi kódot pl ide: /home/ccai01admin/ccaikeret-docs/AI_FRAMEWORK

```bash
#!/usr/bin/env python3
import os
import logging
from flask import Flask, request
import subprocess
import werkzeug

# --- Beállítások ---
LOG_FILE = "/home/ccai01admin/ccaikeret-docs/mkdocs_webhook.log"
DOCS_DIR = "/home/ccai01admin/ccaikeret-docs"
DOCKER_COMPOSE_DIR = os.path.join(DOCS_DIR, "AI_FRAMEWORK")
BRANCH = "develop"
PORT = int(os.environ.get("MKDOCS_WEBHOOK_PORT", 9102))  # default 9102

# --- Logolás ---
os.makedirs(DOCS_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Werkzug log elnyomása
logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

app = Flask(__name__)

@app.route("/payload", methods=["POST"])
def payload():
    data = request.json
    branch_ref = data.get("ref", "")
    logging.info(f"Webhook received for branch: {branch_ref}")

    if branch_ref == f"refs/heads/{BRANCH}":

        # --- Git pull ---
        git_cmd = ["/usr/bin/git", "-C", DOCS_DIR, "pull", "origin", BRANCH]
        try:
            result = subprocess.run(git_cmd, capture_output=True, text=True, check=True)
            logging.info(f"Git pull output:\n{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Git pull failed:\n{e.stderr.strip()}")
            return "Git pull failed", 500

        # --- Docker build + restart ---
        docker_cmd = [
            "docker", "compose",
            "-f", os.path.join(DOCKER_COMPOSE_DIR, "docker-compose.yml"),
            "-f", os.path.join(DOCKER_COMPOSE_DIR, "docker-compose.docs.yml"),
            "up", "-d", "--build", "--force-recreate", "docs"
        ]

        try:
            result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
            logging.info("Docker docs container rebuilt and restarted successfully")
            logging.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error(f"Docker compose failed:\n{e.stderr.strip()}")
            return "Docker update failed", 500

        return "Docs updated", 200

    return "Ignored", 200


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=PORT)
```

Indítás kézzel, később systemd-vel:
```bash
cd /home/ccai01admin/ccaikeret-docs/AI_FRAMEWORK
/home/ccai01admin/ccaikeret/venv/bin/python3 mkdocs_webhook.py
```

##  System service létrehozása
```bash
sudo nano /etc/systemd/system/mkdocs_webhook.service
```

Tegyük bele:

```bash
[Unit]
Description=MkDocs Webhook
After=network.target

[Service]
Type=simple
User=ccai01admin
Group=ccai01admin
WorkingDirectory=/home/ccai01admin/ccaikeret-docs/AI_FRAMEWORK
Environment="PATH=/home/ccai01admin/ccaikeret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="HOME=/home/ccai01admin"
ExecStart=/home/ccai01admin/ccaikeret/venv/bin/python3 /home/ccai01admin/ccaikeret-docs/AI_FRAMEWORK/mkdocs_webhook.py
Restart=no
RestartSec=5s
StandardOutput=null
StandardError=/home/ccai01admin/ccaikeret-docs/mkdocs_webhook_error.log

[Install]
WantedBy=multi-user.target
```
Fontos: az ExecStart az általad használt virtualenv Python-ját mutatja.

##  Jogok átadása a futtatáshoz
```bash
sudo chown -R ccai01admin:ccai01admin /home/ccai01admin/ccaikeret-docs
sudo chmod -R 775 /home/ccai01admin/ccaikeret-docs
```

##  Log file létrehozása
```bash
touch /home/ccai01admin/ccaikeret-docs/mkdocs_webhook.log
```

##  Systemd service engedélyezése és indítása
```bash
sudo systemctl daemon-reload
sudo systemctl enable mkdocs-webhook
sudo systemctl start mkdocs-webhook
```

##  Állapot ellenőrzése
```bash
sudo systemctl status mkdocs-webhook
tail -f /home/ccai01admin/ccaikeret-docs/mkdocs_webhook.log
```

##  GitHub webhook endpoint
```bash
http://docs.devaiclarity.hu:9102/payload
```

Ellenőrzés curl-el:
```bash
curl -X POST http://172.28.10.13:9102/payload -H "Content-Type: application/json" -d "{\"ref\":\"refs/heads/develop\"}"
```

## Hosts fájl beállíás
```bash
sudo nano /etc/hosts
127.0.0.1      docs.devaiclarity.hu  -- ez lokális
172.28.10.13   docs.aiclarity.hu     -- ez pedig a dev
```

## Webhook endpoint beállítás a Git admin felületén

## VPN mögötti ativálás/hívás

Ha vpn mögött vagyunk és nem érhető el a GITHUB felületéről a service, akkor létrekell hozni egy cmd fájl-t és push után futtatni. 
Ez szól a webhook-nak, hogy pullozzon és frissítse a felületet.
Ezt kell beletenni.

```bash
@echo off
echo Updating develop branch...
curl -X POST http://172.28.10.13:9102/payload -H "Content-Type: application/json" -d "{\"ref\":\"refs/heads/develop\"}"
echo.
echo Done.
pause
```

##  SSH kulcs generálás és beállítása
Nézd meg van-e SSH kulcs

```bash
ls ~/.ssh
```
Ha nincs, akkor generáljuk:

id_rsa
id_rsa.pub

```bash
ssh-keygen -t ed25519 -C "docs-server"
```

Public key megjelenítése:
```bash
cat ~/.ssh/id_ed25519.pub
```

Valami ilyesmi lesz:
```bash
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... mkdocs-webhook
```

Másold ki teljesen és add hozzá GitHub-hoz.

Menj ide:
```bash
https://github.com/settings/keys
```

Add New SSH key.

Teszteljük a kapcsolatot
```bash
ssh -T git@github.com
```

Ha jó, akkor ezt fogod látni:
```bash
Hi zelinaclarity! You've successfully authenticated...
```

Repo átállítása SSH-ra:
```bash
cd /home/ccai01admin/ccaikeret-docs
git remote set-url origin git@github.com:CLARITY-CONSULTING-KFT/CLA_AI_KERET_2025.git
```

Teszteljük:
```bash
git pull
```

Ha működik, akkor nem kér user/pass-t és azonnal pull.

##  Develop branch lekérése
```bash
git fetch origin develop

Username for 'https://github.com': zelinaclarity
Password for 'https://zelinaclarity@github.com': <IDE A TOKEN-T MÁSOLD>

```

##  Checkout a develop branch

```bash
git checkout -b develop origin/develop
```
-	Most már a develop branch van a szerveren is 
-	Innentől a CI/CD webhook script tudja frissíteni a docs konténert automatikusan 


##  Teszt git pull
```bash
git pull origin develop
```

##  Tesztelés GitHub webhookkal
Push a develop branch-re 
-	GitHub webhook → Flask endpoint → git pull → logolás 
-	MkDocs --dirtyreload automatikusan frissíti a site-ot 


## HASZNOS PARANCSOK








