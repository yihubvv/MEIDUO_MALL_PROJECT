# MeiDuo Mall Docker Runbook

This Compose stack builds two project images:

- `meiduo-mall-web:latest`: Django/uWSGI application
- `meiduo-mall-nginx:latest`: HTTPS/static frontend proxy

It also starts MySQL, Redis, Elasticsearch, FastDFS tracker, and FastDFS storage.

## Start on a new device

From the project root:

```bash
docker compose build
docker compose up -d
```

Open:

```text
https://www.meiduo.site/
```

For local testing without DNS, map `www.meiduo.site` to the Docker host IP in the client machine's hosts file.

## Database Data

The current MySQL data is exported to:

```text
data/meiduo_mall_current.sql
```

On first `docker compose up`, the MySQL container imports this file automatically through:

```text
/docker-entrypoint-initdb.d/01_meiduo_mall_current.sql
```

MySQL only imports init SQL when its data volume is empty. To reload from the SQL file from scratch:

```bash
docker compose down -v
docker compose up -d
```

## Useful Checks

```bash
docker compose ps
docker compose logs -f web
docker compose exec mysql mysql -uroot -pmysql -D meiduo_mall -e "SELECT COUNT(*) FROM tb_sku;"
curl -k -I --resolve www.meiduo.site:443:127.0.0.1 https://www.meiduo.site/static/js/host.js
```

## Moving Built Images Manually

If the other device should not build from source, export the images:

```bash
docker save meiduo-mall-web:latest meiduo-mall-nginx:latest -o meiduo-mall-images.tar
```

On the other device:

```bash
docker load -i meiduo-mall-images.tar
docker compose up -d
```
