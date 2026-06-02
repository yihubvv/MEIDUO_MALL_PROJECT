# Enable HTTPS for MeiDuo Mall (nginx)

This directory contains an example nginx server block to proxy HTTPS requests to the local Django app running on `127.0.0.1:8000`.

Steps to enable on the host (requires sudo):

1. Copy config to nginx sites directory:

```bash
sudo cp utils/nginx/meiduo_site.conf /etc/nginx/sites-available/meiduo_site.conf
sudo ln -s /etc/nginx/sites-available/meiduo_site.conf /etc/nginx/sites-enabled/meiduo_site.conf
```

2. Create or install TLS certificates. For testing you can create a self-signed cert:

```bash
sudo openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout /etc/ssl/private/meiduo.key \
  -out /etc/ssl/certs/meiduo.crt \
  -subj "/CN=localhost"
```

3. Test nginx config and restart:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

4. (Optional) If you run Django behind `gunicorn`/`uwsgi` on a different socket/port, update the `upstream` block in the config to point to that location.

5. Adjust `server_name` in the config to your production domain and install real certificates (Let’s Encrypt recommended).

Notes
- The example maps `/static/` to `front_end_pc/` — change if your static files are elsewhere.
- For production, prefer a non-root application user rather than proxying as `root`.
