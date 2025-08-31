# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Configure the login manager
# 'main.login' is the function name of our login route
login_manager.login_view = 'main.login' 
login_manager.login_message_category = 'info' # Bootstrap class for flash messages

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind the extensions to the app instance
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import and register the blueprint
    # Blueprints help organize routes, especially in larger apps
    from app.routes import main
    app.register_blueprint(main)

    return app