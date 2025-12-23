from flask import render_template, session, redirect, url_for
from models import *

import random 

moodMultiplier = {
    "cold": 0.6,
    "neutral": 1.0,
    "curious": 1.3,
    "uneasy": 1.5,
    "patient": 0.9,
    "resigned": 2.0
}

def routes(app):

    # moved check to ensure user are same thing
    @app.before_request
    def ensure_user():
        if "userID" not in session:
            user = User()
            db.session.add(user)
            db.session.commit()
            session["userID"] = user.id




    @app.route("/")
    def inbox():
        user = User.query.get(session["userID"]) # get = finds objects based on primary key
        
        if not user:
            session.clear()
            return redirect(url_for("inbox"))
        
        msg = pickMessage(user)

        if not msg: return render_template ("home.html", msg = "Nothing's left for you.", archived = user.archived.all(), exhuasted = True)
        return render_template("home.html", msg = msg, archived = user.archived.all(), exhuasted = False)


    def pickMessage(user):
        # messages = Messages.query.filter_by(tone = user.currentTone).all() # filter_by is used for simple task, and filter for complex ones, and .all() will actually execute query rather than just storing it as query object
        seenList = user.lastSeen or []
        archivedList = [ am.msgID for am in user.archived.all()]
        excludeList = seenList + archivedList

        messages = Messages.query.filter(~Messages.id.in_(excludeList)).all()
        if not messages:
            return None

       # random selection based on user mood levels
        weights = []
        for m in messages:
            # calculate user affinity for that tone
            user_affinity = getattr(user, m.tone, 1) + 1 
            w = m.weight * moodMultiplier.get(m.tone, 1.0) * user_affinity
            weights.append(w)

        return random.choices(messages, weights=weights, k=1)[0]
    
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
        elif choice == "ignore":
            user.cold += 2
            user.patient -= 1
        elif choice == "archive":
            user.neutral += 2
            user.patient += 1
            db.session.add(ArchiveText(msgID=msgID, uID=user.id))
        

        tones =  [
            "cold",
            "neutral",
            "curious",
            "uneasy",
            "patient"
        ]

        markSeen(user, msgID)
        if any(getattr(user,m) >= 30 for m in tones ): 
            for m in tones:
                setattr(user,m,max(0, getattr(user,m) - 5))
        db.session.commit()
        return redirect(url_for("inbox"))

        

            
        
