from flask import g, redirect, render_template, request, url_for
from markupsafe import Markup
from functools import wraps
from debug import *
from zoodb import *

import auth_client as auth   # מדבר עם auth-server.py דרך RPC
import bank_client as bank
import random


class User(object):
    def __init__(self):
        self.person = None
        self.token = None
        self.zoobars = 0

    def checkLogin(self, username, password):
        """
        מנסה להתחבר דרך שירות האימות (auth_svc).
        אם מצליח – מחזיר מחרוזת cookie: "username#token"
        """
        token = auth.login(username, password)
        if token is not None:
            return self.loginCookie(username, token)
        else:
            return None

    def loginCookie(self, username, token):
        """
        מעדכן את ה-user המקומי ויוצר ערך cookie לשמירה בדפדפן.
        """
        self.setPerson(username, token)
        return "%s#%s" % (username, token)

    def logout(self):
        self.person = None
        self.token = None
        self.zoobars = 0

    def addRegistration(self, username, password):
        """
        רישום משתמש חדש:
        1. קורא ל-auth_svc כדי ליצור Cred (סיסמה+salt+token)
        2. אם הצליח – כאן (בתוך zookduser) ניצור רשומת Person ב-DB של person
        3. נחזיר cookie עם username#token
        """
        # 1. קריאה לשירות האימות (auth_svc) – רץ כ-authuser ונוגע רק ב-Cred
        token = auth.register(username, password)
        if token is None:
            return None

        # 2. יצירת Person מתבצעת בצד ה-web app (zookduser) שיש לו גישה ל-person.db
        db = person_setup()
        person = db.query(Person).get(username)
        if not person:
            person = Person()
            person.username = username
            # שדות שלא קשורים לאימות – כאן
            person.zoobars = 10
            person.profile = ""
            db.add(person)
            db.commit()

        # 3. נחזיר cookie (username#token)
        return self.loginCookie(username, token)

    def checkCookie(self, cookie):
        """
        בודק את ה-cookie שמגיע מהדפדפן.
        אם תקין ויש token חוקי – טוען את המשתמש ל-self.person
        """
        if not cookie:
            return

        # לוודא שהפורמט תקין: "username#token"
        if "#" not in cookie:
            return

        (username, token) = cookie.rsplit("#", 1)
        if auth.check_token(username, token):
            self.setPerson(username, token)

    def setPerson(self, username, token):
        """
        טוען את ה-Person מה-DB ומביא את היתרה מהשירות של הבנק.
        """
        persondb = person_setup()
        self.person = persondb.query(Person).get(username)
        self.token = token
        self.zoobars = bank.balance(username)


def logged_in():
    """
    בודק האם המשתמש מחובר לפי ה-cookie.
    """
    g.user = User()
    g.user.checkCookie(request.cookies.get("PyZoobarLogin"))
    if g.user.person:
        return True
    else:
        return False


def requirelogin(page):
    @wraps(page)
    def loginhelper(*args, **kwargs):
        if not logged_in():
            return redirect(url_for('login') + "?nexturl=" + request.url)
        else:
            return page(*args, **kwargs)
    return loginhelper


@catch_err
def login():
    cookie = None
    login_error = ""
    user = User()

    if request.method == 'POST':
        username = request.form.get('login_username')
        password = request.form.get('login_password')

        if 'submit_registration' in request.form:
            if not username:
                login_error = "You must supply a username to register."
            elif not password:
                login_error = "You must supply a password to register."
            else:
                cookie = user.addRegistration(username, password)
                if not cookie:
                    login_error = "Registration failed."
        elif 'submit_login' in request.form:
            if not username:
                login_error = "You must supply a username to log in."
            elif not password:
                login_error = "You must supply a password to log in."
            else:
                cookie = user.checkLogin(username, password)
                if not cookie:
                    login_error = "Invalid username or password."

    nexturl = request.values.get('nexturl', url_for('index'))
    if cookie:
        response = redirect(nexturl)
        ## Be careful not to include semicolons in cookie value; see
        ## https://github.com/mitsuhiko/werkzeug/issues/226 for more
        ## details.
        response.set_cookie('PyZoobarLogin', cookie)
        return response

    return render_template('login.html',
                           nexturl=nexturl,
                           login_error=login_error,
                           login_username=Markup(request.form.get('login_username', '')))


@catch_err
def logout():
    if logged_in():
        g.user.logout()
    response = redirect(url_for('login'))
    response.set_cookie('PyZoobarLogin', '')
    return response
