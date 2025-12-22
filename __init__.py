from flask import Flask
from routes import routes
from models import *
from seedMessages import messages
import os

def createApp():
    app = Flask(__name__)
    # 1. Use Render's environment variable, fallback to local for dev
    # Render's URL starts with postgres://, but SQLAlchemy 1.4+ requires postgresql://
    uri = os.getenv("DATABASE_URL", "postgresql://postgres:6969@localhost:5432/inboxfromnowhere")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "superSecretKey") # Use env var for security

    # #                                       "dialect+driver://username:password@host:port/database"
    # app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:6969@localhost:5432/inboxfromnowhere"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # app.secret_key = "superSecretKey"
    db.init_app(app)
    routes(app)

    with app.app_context():
        db.create_all()
        if Messages.query.first():
            pass
        else:
            for i, message in enumerate(messages, start=1):
                db.session.add(Messages(id=i, **message))
            db.session.commit()

    return app
