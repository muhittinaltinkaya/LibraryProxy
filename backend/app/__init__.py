from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
import redis
import os

# Global extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
bcrypt = Bcrypt()
redis_client = None

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # CORS configuration
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.journals import journals_bp
    from app.routes.proxy import proxy_bp
    from app.routes.admin import admin_bp
    from app.routes.health import health_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(journals_bp, url_prefix='/api/journals')
    app.register_blueprint(proxy_bp, url_prefix='/api/proxy')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app
