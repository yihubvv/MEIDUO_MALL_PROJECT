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

COPY requirements.txt fdfs_client-py-master.zip ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY meiduo_mall ./meiduo_mall
COPY front_end_pc ./front_end_pc
COPY docker/app/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/meiduo_mall/logs /tmp/fdfs

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uwsgi", "--http", "0.0.0.0:8000", "--chdir", "/app/meiduo_mall", "--module", "meiduo_mall.wsgi:application", "--master", "--processes", "4", "--threads", "2", "--enable-threads", "--die-on-term"]
