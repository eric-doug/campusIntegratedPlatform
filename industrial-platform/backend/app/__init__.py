import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

# Ensure shared module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from shared.database.db import db, init_db
from shared.utils.logger import setup_logger

logger = setup_logger('industrial')
migrate = Migrate()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'campus')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'campus_dev_2026')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'industrial')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'change-this-in-production')

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.engine = None  # Will be set by init_app
    from shared.database.db import Database
    database = Database()
    app.extensions['sqlalchemy'] = None  # Reset for Flask-SQLAlchemy compatibility

    # Use shared database engine
    with app.app_context():
        from shared.database.db import Base
        Base.metadata.bind = database.engine

    migrate.init_app(app, db=None)  # We'll handle migrations manually

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.products import products_bp
    from .routes.categories import categories_bp
    from .routes.inquiries import inquiries_bp
    from .routes.orders import orders_bp
    from .routes.suppliers import suppliers_bp
    from .routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/industrial/products')
    app.register_blueprint(categories_bp, url_prefix='/api/industrial/categories')
    app.register_blueprint(inquiries_bp, url_prefix='/api/industrial/inquiries')
    app.register_blueprint(orders_bp, url_prefix='/api/industrial/orders')
    app.register_blueprint(suppliers_bp, url_prefix='/api/industrial/suppliers')
    app.register_blueprint(ai_bp, url_prefix='/api/industrial/ai')

    logger.info("Industrial Platform Backend initialized")
    return app
