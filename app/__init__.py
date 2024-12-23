from flask import Flask
from app.celery_config import make_celery

def create_app():
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = 'redis://default:FaVmdWhoEkgzrfMTWbjByqhTJEvyTDlq@junction.proxy.rlwy.net:57754'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://default:FaVmdWhoEkgzrfMTWbjByqhTJEvyTDlq@junction.proxy.rlwy.net:57754'

    # Initialize Celery
    celery = make_celery(app)

    # Register routes (Blueprints)
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app, celery

# Add this to expose the celery instance
app, celery = create_app()