from app import create_app
from app.celery_config import make_celery

# Create the Flask app and the Celery instance
app, celery = create_app()

# If running from a script, you can start Celery like this (but typically this should be run from the command line):
if __name__ == '__main__':
    celery.start()

