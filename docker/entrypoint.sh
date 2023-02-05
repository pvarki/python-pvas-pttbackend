#!/bin/bash -l
set -e
if [ "$#" -eq 0 ]; then
  # FIXME: can we know the traefik internal docker ip easily ?
  exec gunicorn pttbackend.api:APP --bind 0.0.0.0:8000 --forwarded-allow-ips='*' -w 4 -k uvicorn.workers.UvicornWorker
else
  exec "$@"
fi
