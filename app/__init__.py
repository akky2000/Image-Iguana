from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    if config_class is None:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            app.config.from_object(ProductionConfig)
        elif env == 'testing':
            app.config.from_object(TestingConfig)
        else:
            app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'main.login'  # Use blueprint endpoint

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
