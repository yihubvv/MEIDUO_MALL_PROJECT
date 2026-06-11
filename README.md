# MEIDUO_MALL_PROJECT

This project is based off of a Chinese Web Development project MeiDuo Mall. I mainly focused on building the backend logic. This project emulates the basic logic of generic shopping websites, and uses Django as its web frame. I completed the core functions such as OAUTH login, searching keywords, and managing user cart.

## Skills Used In This Project
- Django
- FastDFS
- Redis
- Elasticsearch
- Haystack
- Crontab
- Redis
- Nginx
- MySQL
- OAUTH
- Celery
- CaptCha

## What I Have Learned In This Project
- Use **Django** and its built-in modules to complete login, logout, authentication logics.
- Use **FastDFS** to handle loads of images.
- Implement keyword search using **Elasticsearch** and **Haystack**.
- Generate static pages using **Crontab** after every set interval to make the site update consistely.
- Use **Redis** to cache data and lower the stress to the server.
- Use **Nginx** to upgrade the protocol to HTTPS instead of HTTP for security.
- Acquire user data from different platforms by **OAUTH**.
- Store data in **MySQL**.
- Use **Celery** and Redis to break down tasks.
- Use libraries like **CaptCha** to dynamically generate verification code.
- Set **transaction** and **rollback** so that if mutiple tables in MySQL are changed and the funnction fails, the changes can be reverted back instead of being partially complete.
- Use **Docker** to set the environment.

## What Improvements I Have Made
- Use **FastDFS** to let tracker check storage availablity and assign upcoming images to storege with more space dynamically.
- Use **pipeline** in Python-Redis when multiple redis commands are needed in one function, this reduces calls to redis and boost performance.
- Access through **Nginx** for more secure access(Not everyone could know what you are seeing).
- Use templates and CronTab such that for pages that displays product details, we don't need to manually create pages over and over again; Instead we generate them all together by using templates.
- Use **uwsgi** to make sure that the conversation between the browser and python project is smooth.
- Use **Docker** to make sure that the configuration is the same on other devices.
- Create files like errors.py, general_response.py for **wording convention**; this way we don't need to go in every file to change the responses and error messages beacuse we can modify these two files.

## Notice
- The OAUTH, sending SMS code, sending Emails and connecting to payment system are made unavailable because it requires private data that is not safe to be shared to others.


## To Run The Project On Different Devices

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
