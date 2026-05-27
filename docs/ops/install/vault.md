# HashiCorp Vault telepítési leírás

**Dátum:** 2026.04.11.  
**Verzió:** v1.0  
**Szerző:** Zelina Attila  

---

## Dokumentum kontroll

| Dátum       | Verzió | Szerző        | Megjegyzés                                   |
|------------|--------|---------------|----------------------------------------------|
| 2026.03.13 | 1.0    | Zelina Attila | Első draft verzió                            |
| 2026.03.13 | 1.1    | Katona Ádám   | Kisebb kiegészítések és Markdown formátumra alakítás |
| 2026.03.25 | 1.1    | Zelina Attila | Telepítések során előjött finomítások átvezetése |

---

## ELŐFELTÉTEL

Előfeltétel:

- Python 3.10 vagy újabb
- Docker Desktop
- Git

Klónozzuk a `CLA_AI_KERET_2025` repository `develop` branch-ét:

```bash
git clone -b develop <repo-url>
```

Ajánlott elérési út:

```
C:/Users/username/GIT/CLA_AI_KERET_2025
```

![](images/vault/media/image10.png)

>    Az `AI_FRAMEWORK` mappában a `.sh` és `.yml` fájlokat Unix karakterkódolásra kell állítani.  
>    Ellenkező esetben Docker futtatáskor hiba léphet fel.

![](images/vault/media/image11.png)


## Python scriptek futtatása

Navigáljunk:

```
AI_FRAMEWORK/start_scripts
```

## Verzió ellenőrzése

    ```bash
    python --version
    ```

A következő parancsot futtasd a szkript elindításához:

```bash
python scan_char_encoding_transform.py <DIR>
```

## Docker indítása

Navigáljunk az `AI_FRAMEWORK` mappába (ahol a `docker-compose.yml` található).

```bash
docker compose up -d # indítás
docker compose ps # listázás
docker compose down -v # leállítás, a volume-ot is törli
docker compose down # leállítás
```

>   Ha olyan image-et használsz, ami a nexusból érkezik, akkor ne felejts el PUTTY-al felcsatlakozni a szerverre
>   és a host fájlban a `172.28.10.13 aiclarity.hu` legyen irányítva!

## Telepítés

Amennyiben Linux alatt telepítünk, abban az esetben másoljuk fel a `hashicorp-vault` mappát a szerverre, ez megtalálható a Git-ben a hashicorp-vault néven

### vault-data mappa létrehozása

```bash
mkdir -p ~/ccaikeret/hashicorp-vault/vault-data
```

### Tulajdonjog beállítása

```bash
sudo chown -R 100:100 /home/ccai01admin/ccaikeret/hashicorp-vault/vault-data
```

### Jogosultság beállítása

```bash
chmod 755 ~/ccaikeret/hashicorp-vault/vault-data
```

### Futtathatóvá tétel

```bash
sudo chmod -R +x /home/ccai01admin/ccaikeret
```


### Docker network létrehozása

```bash
docker network create llmnet
```

### Indítás

A `CLA_AI_KERET_2025\hashicorp-vault` alatt adjuk ki a parancsot
```bash
docker compose up -d
```

### Inicializálás

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault operator init
```

>   A megjelenő Unseal kulcsokat és Root Tokent biztonságosan el kell menteni a kdbx fájlba.
    
### Unseal

![](images/vault/media/image13.png)

![](images/vault/media/image12.png)

```bash
docker exec -it vault vault operator unseal <KEY1>
docker exec -it vault vault operator unseal <KEY2>
docker exec -it vault vault operator unseal <KEY3>
```

Ha:

```
sealed = false
```

akkor a Vault aktív.

![](images/vault/media/image14.png)
    
### HTTPS beállítás

Hosts fájlba:

```
<IP> vault.devaiclarity.hu
```

### Cert-ek beállítása

Másoljuk be a cert fájlokat:

```
hashicorp-vault/nginx/certs/
```

Majd módosítsuk:

```
hashicorp-vault/nginx/nginx.conf
```

### Admin felület

```
https://vault.devaiclarity.hu:8444
```

![](images/vault/media/image15.png)


## Vault beállítások

### Login a vaultba

```bash
docker exec -it vault vault login <ROOT_TOKEN>
```

![](images/vault/media/image16.png)

### Secrets engine engedélyezése

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault secrets enable -path=secret kv-v2
```

![](images/vault/media/image17.png)

### Secretek feltöltése
Aktiváljuk a python virtuális környezetet, ezt már korábban létrehoztuk, pl: AI_FRAMEWORK\venv
```bash
source venv/bin/activate
```
A `CC_MI_keretrendszer.kdbx` fájlnak a `CLA_AI_KERET_2025\hashicorp-vault` szinten kell lennie.
Lépjünk be a hashicorp-vault\kdbx\ mappába.

![](images/vault/media/image18.png)
```bash
python vault_update_from_kdbx.py
```

A vault felületén a következőt kell, hogy lássuk, miután feltötlöttük a secreteket:

![](images/vault/media/image19.png)

### Vault-config beállítások
Ellenőrizzük, hogy a fájlok a `vault-config` mappában megtalálhatóak

![](images/vault/media/image20.png)

### AppRole engedélyezés


```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault auth enable approle
```

## AppRole létrehozása

### IP lekérdezés 

```bash
docker network inspect llmnet
```

--A kép, csak illusztráció
![](images/vault/media/image21.png)

Mivel a vault-ot kell először telepíteni, lekérdezzük az ip tartományt, hogy ezt később feltudjuk használni és beállítani a Framework telepítésnél. 
Fontos, hogy ebben a tartományban kell a többi konténernek is elindulni. Ezt az ip beállítást aktualizálni kell a Framework-ban is.

### Role létrehozás

Most csinálunk egy role-t az agentnek, docker network-ot állítunk be, ez azért fontos, mert csak a docker networkből enged be
klienseket, kívülről nem. És itt is, csak a vault-agent tud lekérdezni, aminek beállítjuk fixen a 172.22.0.42 ip-t.

Fontos megjegyezni, hogy jelen esetben a 162.22... a tartomány, ebben lesznek kiosztva az ip címek a konténeren belül. Erre nagyon kell figyelni, hogy egységesen állítsuk be.
A ...0.42 pedig egy fix ip cím lesz, amit a vault-agent-nek állítunk be a Framework compose fájlban.

>   A docker-compose.yml állományban a `vault-agent`-nek az IP címét `172.22.0.42`-re állítottuk, ellenőrizzük,
>   hogy ez nem változott, valamint, hogy a `subnet` a `172.22.0.0/16` tartományra van állítva

"Linux"
    ```bash
    docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault \
    vault write auth/approle/role/vault-agent-role \
    bind_secret_id=false \
    token_policies="agent-policy" \
    token_period=1h \
    token_ttl=1h \
    token_max_ttl=4h \
    token_bound_cidrs="172.22.0.42/16"
    ```
"Windows (PowerShell)"
    ```bash
    docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault `
    vault write auth/approle/role/vault-agent-role `
    bind_secret_id=false `
    token_policies="agent-policy" `
    token_period=1h `
    token_ttl=1h `
    token_max_ttl=4h `
    token_bound_cidrs="172.22.0.42/16"
    ```
![](images/vault/media/image22.png)

### Role lekérdezése

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault read auth/approle/role/vault-agent-role
```

![](images/vault/media/image23.png)

### Role ID lekérdezése

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault read auth/approle/role/vault-agent-role/role-id
```

![](images/vault/media/image24.png)

A role_id-t el kell menteni.

### Policy feltöltés, frissítés

```bash
ccai01admin@ccai01keret:~/ccaikeret/vault-agent$ docker exec -it vault vault policy write agent-policy /vault/config/agent-policy.hcl
```

## Vault Agent integráció (AppRole)

A rendszer a `HashiCorp Vault Agent` segítségével tölti be a konténerek számára szükséges érzékeny adatokat (jelszavak, API kulcsok, tokenek). A Vault Agent AppRole autentikációval (role_id) csatlakozik a Vault szerverhez, majd a szükséges titkokat fájlok formájában elérhetővé teszi a konténerek számára.
A cél az, hogy se jelszó, se API kulcs ne szerepeljen a docker-compose fájlban vagy environment változókban, hanem minden titok dinamikusan a Vaultból kerüljön betöltésre.

A Vault Agent:

1. Autentikál a Vault szerverhez
2. Titkokat lekér
3. Fájlba renderel
4. Más konténerek számára elérhetővé teszi

A titkok tmpfs Docker volume-ba kerülnek.
![](images/vault/media/image33.png)


### Template alapú secret generálás

A Vault Agent template rendszere segítségével a Vaultban tárolt titkok fájlokká kerülnek renderelésre.

Példa template logika:

```bash
{% raw %}
{{ with secret "secret/data/openwebui" }}
{{ .Data.data.password }}
{{ end }}
{% endraw %}
```

A template fájlok helye: `AI_FRAMEWORK/vault-agent/templates`


### Vault-agent.hcl

Az alábbi helyen érhetőel `AI_FRAMEWORK/vault-agent/vault-agent.hcl`
!!! info "Template" 
    Új komponens esetén bővíteni kell a `vault-agent.hcl`-t 

- AppRole autentikációval belép a Vaultba (`auth/approle`)
- A tokent fájlba menti: `/secrets/.vault-token`
- Secretet template alapján fájlba renderel pl.:
    - `openwebui_db_password`
    - `ldap_readonly_user_password`
    - `ldap_admin_password`
- Sikeres autentikáció és renderelés után kilép (`exit_after_auth = true`)

### Agent-policy.hcl

A policy definiálja:

- Milyen secret pathokat érhet el az alkalmazás
- Milyen műveleteket végezhet (read, list, create stb.)

A Vault Agent az AppRole autentikáció után kap egy `Vault tokent`, amelyre ez a policy érvényes.


### Role_id lekérdezése és beállítása

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault read auth/approle/role/vault-agent-role/role-id
```

A lekérdezett role_id-t be kell másolni a `AI_FRAMEWORK/vault-agent/role_id` fájl-ba.
![](images/vault/media/image34.png)
 

### Konténerek ip tartományának beállítása a compose fájlban

A `AI_FRAMEWORK/docker-compose.yml` állományban a `172.19.0.0/16` IP tartomány kell, hogy szerepeljen
 ![](images/vault/media/image35.png)

### Memóriában tárolt temp létrehozása a compose fájlban

 ![](images/vault/media/image36.png)
 

### Secrets törlése
A rendszer tartalmaz egy cleanup konténert is: `vault-cleanup`. Ez 180 másodperc után törli a secret fájlokat:
`rm -rf /secrets/*`. Ez további biztonsági réteget ad a rendszerhez.

 ![](images/vault/media/image37.png)

### Vault agent létrehozása a konténerben

Korábban a vault-ban beállítottuk, hogy a `172.19.0.42`-es ip-ről és role_id-val autentikált tokennel lehet csak lekérdezni a secret-eket. Ez a beállítás fontos, hogy összhangban legyen a vault-ban leírtakkal.
A konténer egyszer megfut, betölti a titkokat, megáll és nem indul újra.

 ![](images/vault/media/image38.png)


## LDAP integráció

Fontos megjegyezni, hogy az LDAP integrációhoz szükséges elindítani az LDAP-ot, amit jelenleg még nem lehetséges.
Ha sikeresen feltelepítettük a Vault-ot és integráltuk a Framework-ot, akkor az LDAP is sikeresen elindul. Ezt követően kell az alábbi integrációt elvégezni.


### LDAP engedélyezése

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault auth enable ldap
```
![](images/vault/media/image25.png)

### LDAP konfigurálása

    ```bash
    docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault \
    vault write auth/ldap/config \
    url="ldap://openldap:389" \
    userdn="ou=users,dc=clarity,dc=hu" \
    groupdn="ou=groups,dc=clarity,dc=hu" \
    binddn="cn=admin,dc=clarity,dc=hu" \
    bindpass="********" \
    starttls=false \
    insecure_tls=true \
    userattr="uid"
    ```

### Policy betöltés

```bash
docker exec -it vault vault policy write llm-admins /vault/ldap/llm-admins.hcl
```

### Csoport-policy hozzárendelés az LDAP-hoz

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault write auth/ldap/groups/llm-admins policies="llm-admins"
```

### Token lejárat beállítása

Ha Alice megváltoztatja az LDAP jelszavát, a régi Vault tokenje még működik a lejáratig, ez Vault design.
Ezért csökkenteni kell a token lejáratát, így jelszócsere után max 1 órán belül minden session megszűnik.

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault login <ROOT_TOKEN_ID>
```
```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault vault auth tune -default-lease-ttl=1h -max-lease-ttl=24h ldap/
```

![](images/vault/media/image31.png)

### Ellenőrzés

```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -it vault  vault auth list -detailed
```

![](images/vault/media/image32.png)


## HASZNOS PARANCSOK

### LLMNETRE terelés:

```bash
docker network connect llmnet vault
```

### 9.2	Futtatási jog beállítás egy sh fájlra

```bash
chmod +x litellm-oauth2-proxy/litellm-oauth-secrets.sh
```
	
### Nexusra kapcsolódás

```bash
docker login aiclarity.hu:8443
```

### AppRole lekérdezés

```bash
docker exec -it vault vault list auth/approle/role
```

### Olvasd ki a token policy-t:

```bash
docker exec -it vault  vault read auth/approle/role/vault-agent-role
```

### Docker vault-agent ip lekérdezés

```bash
{% raw %}
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' vault-agent
{% endraw %}
```

### Másik szerverről elérés konfiguráció

### Vault CLI telepítése

```bash
sudo apt update
sudo apt install -y gpg curl software-properties-common

curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update
sudo apt install vault
```

### Utána ellenőrzés

vault version

### Vault elérésének tesztelése

Nginx-en keresztül lehet elérni a vault-ot, teszteljük le:

```bash
curl -k https://ipcím:8444/v1/sys/health
```

### Vault integráció (Vault Agent)

[Vault Agent](../components/vault.md)








