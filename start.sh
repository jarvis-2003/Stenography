#!/bin/bash

# Start the Flask app
flask --app app:app run --host=0.0.0.0 --port=$PORT &

# Start the Celery worker
celery -A worker.celery worker --pool=solo -l info
