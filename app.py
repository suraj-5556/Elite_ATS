import os
import logging
from flask import Flask
from app.routes.main import main_bp
from app.routes.resume import resume_bp
from app.routes.jobs import jobs_bp
from app.routes.match import match_bp
from app.routes.dashboard import dashboard_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    app.config['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')

    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('experiments', exist_ok=True)

    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(match_bp, url_prefix='/match')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
