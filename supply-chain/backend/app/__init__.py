import os
import sys
from flask import Flask
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
from shared.database.db import db
from shared.utils.logger import setup_logger

logger = setup_logger('supply_chain')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'campus')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'campus_dev_2026')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'supply_chain')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'change-this-in-production')

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from .routes.warehouses import warehouses_bp
    from .routes.inbound import inbound_bp
    from .routes.outbound import outbound_bp
    from .routes.inventory import inventory_bp
    from .routes.vessels import vessels_bp
    from .routes.shipments import shipments_bp
    from .routes.ai_routes import ai_bp

    app.register_blueprint(warehouses_bp, url_prefix='/api/supply/warehouses')
    app.register_blueprint(inbound_bp, url_prefix='/api/supply/inbound')
    app.register_blueprint(outbound_bp, url_prefix='/api/supply/outbound')
    app.register_blueprint(inventory_bp, url_prefix='/api/supply/inventory')
    app.register_blueprint(vessels_bp, url_prefix='/api/supply/vessels')
    app.register_blueprint(shipments_bp, url_prefix='/api/supply/shipments')
    app.register_blueprint(ai_bp, url_prefix='/api/supply/ai')

    logger.info("Supply Chain Platform Backend initialized")
    return app
