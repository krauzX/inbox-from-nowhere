from flask import Flask
from routes import routes
from models import *


def createApp():
    app = Flask(__name__)
    #                                       "dialect+driver://username:password@host:port/database"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:6969@localhost:3306/inboxfromnowhere"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "superSecretKey"
    db.init_app(app)
    routes(app)

    with app.app_context():
        db.create_all()

    return app
