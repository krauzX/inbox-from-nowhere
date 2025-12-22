from flask import render_template, session, redirect, url_for
from models import *

import random 

moodMultiplier = {
    "cold": 0.6,
    "neutral": 1.0,
    "curious": 1.3,
    "uneasy": 1.5,
    "patient": 0.9
}

def routes(app):

    @app.before_request
    def ensure_user():
        uid = session.get("userID")

        if uid:
            user = User.query.get(uid)
            if user:
                return  # user is valid

        user = User()
        db.session.add(user)
        db.session.commit()
        session["userID"] = user.id




    @app.route("/")
    def inbox():
        if "userID" not in session:
            user = User()
            db.session.add(user)
            db.session.commit()
            session["userID"] = user.id 
        
        user = User.query.get(session["userID"]) #get = finds objects based on primary key
        msg = pickMessage(user)
        if not msg: return render_template ("home.html", msg = "Nothing's left for you.", archived = user.archives, exhuasted = True)
        return render_template("home.html", msg = msg, archived = user.archived.all(), exhuasted = False)


    def pickMessage(user):
        # messages = Messages.query.filter_by(tone = user.currentTone).all() # filter_by is used for simple task, and filter for complex ones, and .all() will actually execute query rather than just storing it as query object
        seenList = user.lastSeen or []
        archivedList = [ am.msgID for am in user.archived.all()]
        excludeList = seenList + archivedList

        messages = Messages.query.filter(~Messages.id.in_(excludeList)).all()
        if not messages: return None

        weights = [message.weight * moodMultiplier.get(message.tone, 1) for message in messages]
        msg = random.choices(messages, weights = weights, k = 1 )[0] # choice is for equal prob selection and choices for weighted one, first will take objects, second will their weights, k tells how many object to pick, since it returns list of objects, now we picking first object
        return msg
    
    def markSeen(user, msgID, limit = 5):
        seenList = user.lastSeen or [] 
        seenList.append(msgID)
        user.lastSeen = seenList[-limit:]
        

    
    @app.route("/act/<choice>/<int:msgID>")
    def act(choice, msgID):
        user = User.query.get(session["userID"])

        if choice == "open":
            user.curious += 2
            user.uneasy += 1
            user.cold = max(0, user.cold - 1)

        elif choice == "ignore":
            user.cold += 2
            user.uneasy += 1
            user.patient = max(0, user.patient - 1)
        
        elif choice == "archive":
            user.neutral += 2
            user.patient += 1
            user.uneasy = max(0, user.uneasy - 1)

            archivedMsg = ArchiveText(msgID = msgID, uID = user.id)
            db.session.add(archivedMsg)
        

        tones =  {
            "cold": user.cold,
            "neutral": user.neutral,
            "curious": user.curious,
            "uneasy": user.uneasy,
            "patient": user.patient
        }

        if max(tones.values()) >= 30: clamp(user)
        markSeen(user, msgID)
        db.session.commit()

        return redirect(url_for("inbox"))

    def clamp(user, maxVal=25):
        for mood in ["cold", "neutral", "curious", "uneasy", "patient"]:
            val = getattr(user, mood)
            if val > maxVal:
                setattr(user, mood, maxVal)
            else:
                setattr(user, mood, max(0, val - 1))


            
        
