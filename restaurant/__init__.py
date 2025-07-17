from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .routes import main 


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    #app.config.from_pyfile('../instance/config.py')
    
    #db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    
    return app
