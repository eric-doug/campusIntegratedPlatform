import os
import sys
from flask import Flask
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
from shared.database.db import db
from shared.utils.logger import setup_logger

logger = setup_logger('park_service')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'campus')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'campus_dev_2026')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'park_service')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'change-this-in-production')

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from .routes.enterprises import enterprises_bp
    from .routes.energy import energy_bp
    from .routes.safety import safety_bp
    from .routes.emission import emission_bp
    from .routes.reports import reports_bp
    from .routes.submissions import submissions_bp
    from .routes.ai_routes import ai_bp

    app.register_blueprint(enterprises_bp, url_prefix='/api/park/enterprises')
    app.register_blueprint(energy_bp, url_prefix='/api/park/energy')
    app.register_blueprint(safety_bp, url_prefix='/api/park/safety')
    app.register_blueprint(emission_bp, url_prefix='/api/park/emission')
    app.register_blueprint(reports_bp, url_prefix='/api/park/reports')
    app.register_blueprint(submissions_bp, url_prefix='/api/park/submissions')
    app.register_blueprint(ai_bp, url_prefix='/api/park/ai')

    logger.info("Park Service Platform Backend initialized")
    return app
