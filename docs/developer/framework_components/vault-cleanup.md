# Vault Cleanup

## Cél

A vault-cleanup egy segéd konténer, amely:
- időzítve törli a Vault által kiírt secret fájlokat
- csökkenti a secret-ek élettartamát a fájlrendszeren
- növeli a biztonságot

## Compose szerep

- image: `busybox`
- restart: `no`

## Függőségek

- `vault-agent`

## Parancs

- `sleep 180 && rm -rf /secrets/*`

## Vault cleanup compose

```bash  
  vault-cleanup:
    image: busybox
    depends_on:
      - vault-agent
    volumes:
      - vault-secrets:/secrets:rw
    command: sh -c "sleep 180 && rm -rf /secrets/*"
    restart: "no"   
```
### Alapadatok

| Tulajdonság    | Érték         | Magyarázat                                                                 |
| -------------- | ------------- | -------------------------------------------------------------------------- |
| Service név    | vault-cleanup | A Compose-on belüli logikai név. Nem publikus service, csak háttérfeladat. |
| Image          | busybox       | Minimalista Linux image, ideális egyszerű shell parancsok futtatására.     |
| Restart policy | no            | Nem indul újra automatikusan → egyszer fut le, majd kilép.                 |
| Függőség       | vault-agent   | Csak akkor indul, ha a Vault Agent már lefutott és kiírta a secret-eket.   |

### Volume

| Volume        | Cél      | Típus |
| ------------- | -------- | ----- |
| vault-secrets | /secrets | RW    |

Ez ugyanaz a volume, amit más service-ek is használnak:

- LiteLLM
- Grafana
- OpenLDAP, stb

### Mit csinál?

| Lépés             | Jelentés                           |
| ----------------- | ---------------------------------- |
| sleep 180       | 180 másodperc (3 perc) várakozás |
| rm -rf /secrets/* | minden secret törlése a volume-ból |

### Kockázatok

| Kockázat         | Magyarázat                    |
| ---------------- | ----------------------------- |
| Túl korai törlés | app még használja a secret-et |
| Nincs újratöltés | ha app nem refresh-el         |

