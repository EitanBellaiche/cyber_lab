from zoodb import *
from debug import *

import os
import hashlib
import random
import pbkdf2   # הקובץ pbkdf2.py נמצא בתיקיית zoobar


# פונקציה לעשיית hash לסיסמה עם salt (מתאימה ל-Python 3)
def hash_password(password, salt):
    # pbkdf2 במעבדה נכתבה ל-Python 2, אז נוודא שהכול בבייטים
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(salt, str):
        salt = salt.encode('utf-8')
    return pbkdf2.PBKDF2(password, salt).hexread(32)


def newtoken(cdb, cred):
    """
    מייצר token חדש עבור המשתמש ושומר אותו בשדה cred.token
    """
    hashinput = "%s%.10f" % (cred.password, random.random())
    if isinstance(hashinput, str):
        hashinput_bytes = hashinput.encode('utf-8')
    else:
        hashinput_bytes = hashinput
    cred.token = hashlib.md5(hashinput_bytes).hexdigest()
    cdb.commit()
    return cred.token


def login(username, password):
    """
    בדיקת התחברות:
    - לוקח את ה-Cred של המשתמש
    - מחשב hash(password + salt)
    - משווה לערך השמור
    - אם הצליח – יוצר token חדש ומחזיר אותו
    """
    cdb = cred_setup()
    cred = cdb.query(Cred).get(username)
    if not cred:
        return None

    # תמיכה במצב ישן ללא salt (אם בכלל קיים)
    if not getattr(cred, 'salt', None):
        if cred.password != password:
            return None
        return newtoken(cdb, cred)

    # משתמש חדש עם salt + hash
    hashed_input = hash_password(password, cred.salt)
    if hashed_input != cred.password:
        return None

    return newtoken(cdb, cred)


def register(username, password):
    """
    רישום משתמש חדש *רק* בטבלת Cred.
    יצירת ה-Person נעשית ע"י קוד ה-web (login.py) שרץ כ-zookduser.

    כאן:
    - נוודא שאין כבר Cred למשתמש הזה
    - ניצור salt רנדומלי
    - נשמור hash(password+salt) + salt בטבלת Cred
    - ניצור token חדש ונחזיר אותו
    """
    cdb = cred_setup()

    # אם כבר יש Cred למשתמש – נכשל
    if cdb.query(Cred).get(username):
        return None

    # salt קריפטוגרפי
    salt_bytes = os.urandom(16)
    salt = salt_bytes.hex()  # נשמור את ה-salt כמחרוזת hex
    hashed = hash_password(password, salt)

    cred = Cred()
    cred.username = username
    cred.password = hashed   # כאן נשמר ה-hash (לא הסיסמה עצמה)
    cred.salt = salt
    cred.token = None

    cdb.add(cred)
    cdb.commit()

    return newtoken(cdb, cred)


def check_token(username, token):
    """
    בדיקה האם ה-token שסופק מתאים ל-token השמור ב-Cred.
    """
    cdb = cred_setup()
    cred = cdb.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False
