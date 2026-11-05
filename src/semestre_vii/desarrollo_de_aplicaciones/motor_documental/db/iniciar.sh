#!/bin/sh
set -eu
mkdir -p /credenciales /clave_api
for archivo in /credenciales/postgres /clave_api/clave; do
    if [ ! -s "$archivo" ]; then
        head -c 48 /dev/urandom | base64 | tr -d '\n' > "$archivo"
        chmod 644 "$archivo"
    fi
done
exec /usr/local/bin/docker-entrypoint.sh postgres
