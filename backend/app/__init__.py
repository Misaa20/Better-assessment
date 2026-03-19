import logging
import uuid

from flask import Flask, g, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

logger = logging.getLogger("fairsplit")


def create_app(config_name="default"):
    app = Flask(__name__)

    from app.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    CORS(app)

    _setup_logging(app)
    _register_middleware(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    return app


def _setup_logging(app):
    log_level = app.config.get("LOG_LEVEL", "INFO")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s | %(message)s",
    )
    handler.setFormatter(formatter)
    logging.root.handlers = [handler]
    logging.root.setLevel(getattr(logging, log_level))


def _register_middleware(app):
    @app.before_request
    def attach_request_id():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

    @app.after_request
    def log_response(response):
        logger.info(
            "method=%s path=%s status=%s",
            request.method,
            request.path,
            response.status_code,
            extra={"request_id": g.get("request_id", "N/A")},
        )
        response.headers["X-Request-ID"] = g.get("request_id", "")
        return response


def _register_blueprints(app):
    from app.api.groups import groups_bp
    from app.api.expenses import expenses_bp
    from app.api.settlements import settlements_bp

    app.register_blueprint(groups_bp, url_prefix="/api/groups")
    app.register_blueprint(expenses_bp, url_prefix="/api/expenses")
    app.register_blueprint(settlements_bp, url_prefix="/api/settlements")


def _register_error_handlers(app):
    from app.errors import DomainError

    @app.errorhandler(DomainError)
    def handle_domain_error(exc):
        logger.warning(
            "Domain error: %s (code=%s)",
            exc.message,
            exc.error_code,
            extra={"request_id": g.get("request_id", "N/A")},
        )
        return {"error": exc.message, "code": exc.error_code}, exc.status_code

    @app.errorhandler(422)
    def handle_validation_error(exc):
        return {"error": "Validation failed", "details": exc.description}, 422

    @app.errorhandler(404)
    def handle_not_found(exc):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def handle_internal_error(exc):
        logger.exception(
            "Unhandled error",
            extra={"request_id": g.get("request_id", "N/A")},
        )
        return {"error": "Internal server error"}, 500
