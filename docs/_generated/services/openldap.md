# openldap

**Image:** `osixia/openldap:1.5.0`

## Ports

- `389:389`
- `636:636`

## Environment

- `TZ` = `${TZ:-Europe/Budapest}`
- `LDAP_ORGANISATION` = `${LDAP_ORGANISATION:-Companie}`
- `LDAP_DOMAIN` = `${LDAP_DOMAIN:-Companie.com}`
- `LDAP_ADMIN_PASSWORD_FILE` = `/run/secrets/ldap_admin_password`
- `LDAP_READONLY_USER` = `true`
- `LDAP_READONLY_USER_USERNAME` = `ldapreadonly`
- `LDAP_READONLY_USER_PASSWORD_FILE` = `/run/secrets/ldap_readonly_user_password`
- `LDAP_BASE_DN` = `${LDAP_BASE_DN}`
- `LDAP_ADMIN_DN` = `${LDAP_ADMIN_DN}`
- `LDAP_URI` = `${LDAP_URI:-ldap://localhost:389}`
- `DEFAULT_POLICY_DN` = `${DEFAULT_POLICY_DN}`

## Secrets

- `ldap_admin_password` (./secrets/ldap_admin_password)
- `ldap_readonly_user_password` (./secrets/ldap_readonly_user_password)

## Volumes

- `ldap_data:/var/lib/ldap`
- `ldap_config:/etc/ldap/slapd.d`
- `./ldap/patches:/patches:ro`
