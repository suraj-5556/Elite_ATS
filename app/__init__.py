"""
TalentAI - Application Factory
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

login_manager = LoginManager()


def create_app(config_override=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/talentai')

    if config_override:
        app.config.update(config_override)

    from app.database import init_db
    init_db(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import UserLoader
        return UserLoader.load(user_id)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.auth import auth_bp
    from app.auth.routes import register, login, logout  # ensure routes are loaded
    app.register_blueprint(auth_bp)

    from app.dashboard import dashboard_bp
    from app.dashboard import routes as _dr  # noqa
    app.register_blueprint(dashboard_bp)

    from app.jobs import jobs_bp
    from app.jobs import routes as _jr  # noqa
    app.register_blueprint(jobs_bp)

    from app.match import match_bp
    from app.match import routes as _mr  # noqa
    app.register_blueprint(match_bp)

    from flask import redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    logger.info("TalentAI initialized.")
    return app
