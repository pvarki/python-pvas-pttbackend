#!/bin/bash -l
set -e
if [ "$#" -eq 0 ]; then
  alembic upgrade head
else
  exec "$@"
fi
