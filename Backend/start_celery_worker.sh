#!/bin/bash

set -o errexit
set -o nounset

celery -A svc.celery purge -f -Q insert_index_to_vector_db_queue,query_index_queue &
celery -A svc.celery worker -E -l info --concurrency=10 --pool=gevent -Q insert_index_to_vector_db_queue -n insert_index_to_vector_db_worker &
celery -A svc.celery worker -E -l info --concurrency=10 --pool=gevent -Q query_index_queue -n query_index_worker