FROM nginx:1.25-alpine

RUN apk add --no-cache openssl \
    && mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/meiduo.key \
        -out /etc/nginx/ssl/meiduo.crt \
        -subj "/CN=www.meiduo.site"

COPY docker/nginx/meiduo.conf /etc/nginx/conf.d/default.conf
COPY front_end_pc /app/front_end_pc

EXPOSE 80 443 8080
