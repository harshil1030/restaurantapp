from flask import Flask

def create_app():
    app = Flask(__name__)
    #app.config.from_pyfile('../instance/config.py') 
    
    #db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    
    return app
