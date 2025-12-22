from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Messages(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable = False)
    tone = db.Column(db.String(15), nullable = False)
    weight = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"{self.id} : {self.text} ( {self.tone} )"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    cold = db.Column(db.Integer, default=0)
    neutral = db.Column(db.Integer, default=0)
    curious = db.Column(db.Integer, default=0)
    uneasy = db.Column(db.Integer, default=0)
    patient = db.Column(db.Integer, default=0)

    archived = db.relationship("ArchiveText", backref = "user" , lazy = "dynamic" ) #basically query which is stored as relationship, aka user.archived = SELECT * FROM archive WHERE user.iD = uID 
    # lastSeen = db.Column(db.JSON, default=list) risky as all users will share a single list 
    lastSeen = db.Column(db.JSON, default= lambda:[]) 

    
class ArchiveText(db.Model):
    __tablename__ = "archives"

    id = db.Column(db.Integer, primary_key=True)
    msgID = db.Column(db.Integer, db.ForeignKey("messages.id") )
    uID = db.Column(db.Integer, db.ForeignKey("users.id") ) #refer to table name
    message = db.relationship("Messages")

