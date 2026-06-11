#!/bin/sh
set -eu

wait_for_port() {
    host="$1"
    port="$2"
    name="$3"

    echo "Waiting for ${name} at ${host}:${port}..."
    until nc -z "$host" "$port"; do
        sleep 2
    done
}

MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
REDIS_HOST="$(printf '%s' "${REDIS_URL:-redis://127.0.0.1:6379}" | sed -E 's#^[a-z]+://([^:/]+).*#\1#')"
REDIS_PORT="$(printf '%s' "${REDIS_URL:-redis://127.0.0.1:6379}" | sed -E 's#^[a-z]+://[^:/]+:([0-9]+).*#\1#')"
FDFS_TRACKER_SERVER="${FDFS_TRACKER_SERVER:-tracker:22122}"

wait_for_port "$MYSQL_HOST" "$MYSQL_PORT" "MySQL"
wait_for_port "$REDIS_HOST" "$REDIS_PORT" "Redis"

python - <<'PY'
import os
from pathlib import Path

source = Path('/app/meiduo_mall/utils/fastdfs/client.conf')
target = Path('/tmp/fdfs/client.conf')
tracker = os.environ.get('FDFS_TRACKER_SERVER', 'tracker:22122')

lines = []
for line in source.read_text().splitlines():
    if line.startswith('tracker_server='):
        lines.append('tracker_server={}'.format(tracker))
    elif line.startswith('base_path='):
        lines.append('base_path=/tmp/fdfs')
    else:
        lines.append(line)

target.parent.mkdir(parents=True, exist_ok=True)
target.write_text('\n'.join(lines) + '\n')
PY

export FDFS_CLIENT_CONF="${FDFS_CLIENT_CONF:-/tmp/fdfs/client.conf}"

cd /app/meiduo_mall
python manage.py migrate --noinput

exec "$@"
