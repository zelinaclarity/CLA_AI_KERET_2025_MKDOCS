# central-logger

**Image:** `rsyslog/syslog_appliance_alpine:8.36.0-3.7`

## Ports

- `5514:5514/udp`
- `5514:5514/tcp`

## Environment

- `TZ` = `Europe/Budapest`

## Volumes

- `./rsyslog/rsyslog.conf:/etc/rsyslog.conf:ro`
- `./rsyslog/conf.d:/etc/rsyslog.d:ro`
- `central-logger-logs:/var/log`
- `central-logger-work:/work`
- `central-logger-config:/config`
- `central-logger-logs2:/logs`
