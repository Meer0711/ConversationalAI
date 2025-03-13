#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

#gunicorn svc.main:app --workers 8 --threads 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

uvicorn svc.main:app --host 0.0.0.0 --port 8000 --reload