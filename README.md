# MEIDUO_MALL_PROJECT

MeiDuo Mall is a Django e-commerce project with a static frontend, MySQL data, Redis, Elasticsearch, and FastDFS image storage. The easiest way to run the same project on another laptop is Docker Compose.

## What Another Laptop Needs

Install these first:

- Docker Desktop, or Docker Engine with Docker Compose
- Git, if cloning from a repository
- At least 4 GB free RAM for MySQL, Redis, Elasticsearch, FastDFS, Django, and Nginx

The project includes the current MySQL dump at:

```text
data/meiduo_mall_current.sql
```

Docker imports that SQL file automatically the first time the MySQL container starts.

## Copy Or Clone The Project

On the other laptop, get the whole project folder. For example:

```bash
git clone <your-repo-url> MEIDUO_MALL_PROJECT
cd MEIDUO_MALL_PROJECT
```

If you are copying the folder manually, make sure these files are included:

```text
Dockerfile
docker-compose.yml
requirements.txt
docker/
front_end_pc/
meiduo_mall/
data/meiduo_mall_current.sql
fdfs_client-py-master.zip
```

## Map The Local Domain

The frontend expects `www.meiduo.site`. Add it to the laptop's hosts file.

Linux/macOS:

```bash
sudo sh -c 'echo "127.0.0.1 www.meiduo.site meiduo.site" >> /etc/hosts'
```

Windows PowerShell as Administrator:

```powershell
Add-Content C:\Windows\System32\drivers\etc\hosts "127.0.0.1 www.meiduo.site meiduo.site"
```

If another phone or laptop will access this machine, map `www.meiduo.site` to this machine's LAN IP on that client device instead of `127.0.0.1`.

## Build And Start

From the project root:

```bash
docker compose build
docker compose up -d
```

Then open:

```text
https://www.meiduo.site/
```

The HTTPS certificate is self-signed, so the browser will show a warning. Continue to the site for local development.

## Verify The Project Is Running

Check all containers:

```bash
docker compose ps
```

Check that Django is healthy:

```bash
docker compose exec web python /app/meiduo_mall/manage.py check
```

Check that the imported MySQL data exists:

```bash
docker compose exec mysql mysql -uroot -pmysql -D meiduo_mall -e "SELECT COUNT(*) FROM tb_sku; SELECT COUNT(*) FROM tb_users;"
```

Check that Nginx serves static files:

```bash
curl -k -I --resolve www.meiduo.site:443:127.0.0.1 https://www.meiduo.site/static/js/host.js
```

Expected signs:

- HTTP status is `200`
- `server` is `nginx`
- `content-type` is JavaScript

Check the old HTTP entry point redirects to HTTPS:

```bash
curl -I --resolve www.meiduo.site:8080:127.0.0.1 http://www.meiduo.site:8080/
```

Expected sign:

```text
Location: https://www.meiduo.site/
```

## Reset And Re-import The Database

MySQL imports `data/meiduo_mall_current.sql` only when the Docker volume is empty. To reset everything and import the SQL again:

```bash
docker compose down -v
docker compose up -d
```

## Stop The Project

```bash
docker compose down
```

## Move Built Images Without Rebuilding

On the original machine:

```bash
docker save meiduo-mall-web:latest meiduo-mall-nginx:latest -o meiduo-mall-images.tar
```

Move `meiduo-mall-images.tar` and this project folder to the other laptop. On that laptop:

```bash
docker load -i meiduo-mall-images.tar
docker compose up -d
```

More Docker-specific notes are in `docker/README.md`.
