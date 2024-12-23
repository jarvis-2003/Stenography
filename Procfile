web: flask --app app:app run --host=0.0.0.0 --port=$PORT
worker: celery -A worker.celery worker --pool=solo -l info
