# promtail

**Image:** `grafana/promtail:3.0.0`

## Depends on

- `loki`

## Volumes

- `./promtail/config.yml:/etc/promtail/config.yml:ro`
- `/var/lib/docker/containers:/var/lib/docker/containers:ro`
- `/var/run/docker.sock:/var/run/docker.sock:ro`
- `promtail_data:/tmp`
