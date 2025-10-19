from flask import Flask
from .routes import main
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")
    app.register_blueprint(main)  # Register your routes
    return app
