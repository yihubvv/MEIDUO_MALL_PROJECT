FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN python -m lib2to3 -w /usr/local/lib/python3.12/site-packages/fdfs_client >/dev/null \
    && python - <<'PY'
from pathlib import Path

connection = Path('/usr/local/lib/python3.12/site-packages/fdfs_client/connection.py')
text = connection.read_text()
text = text.replace("return (''.join(recv_buff), total_size)", "return (b''.join(recv_buff), total_size)")
connection.write_text(text)

tracker = Path('/usr/local/lib/python3.12/site-packages/fdfs_client/tracker_client.py')
text = tracker.read_text()
text = text.replace("store_serv.group_name = group_name.strip('\\x00')", "store_serv.group_name = group_name.strip(b'\\x00').decode()")
text = text.replace("store_serv.ip_addr = ip_addr.strip('\\x00')", "store_serv.ip_addr = ip_addr.strip(b'\\x00').decode()")
tracker.write_text(text)

storage = Path('/usr/local/lib/python3.12/site-packages/fdfs_client/storage_client.py')
text = storage.read_text()
text = text.replace("file_ext_name = str(file_ext_name) if file_ext_name else ''", "file_ext_name = str(file_ext_name).encode() if file_ext_name else b''")
text = text.replace("remote_filename = remote_name.strip('\\x00')", "remote_filename = remote_name.strip(b'\\x00').decode()")
text = text.replace("'Group name'      : group_name.strip('\\x00')", "'Group name'      : group_name.strip(b'\\x00').decode()")
text = text.replace("'Remote file_id'  : group_name.strip('\\x00') + os.sep + \\", "'Remote file_id'  : group_name.strip(b'\\x00').decode() + os.sep + \\")
storage.write_text(text)
PY
RUN find /usr/local/lib/python3.12/site-packages/fdfs_client -name '*.bak' -delete

COPY meiduo_mall ./meiduo_mall
COPY front_end_pc ./front_end_pc
COPY docker/app/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/meiduo_mall/logs /tmp/fdfs

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uwsgi", "--http", "0.0.0.0:8000", "--chdir", "/app/meiduo_mall", "--module", "meiduo_mall.wsgi:application", "--master", "--processes", "4", "--threads", "2", "--enable-threads", "--die-on-term"]
