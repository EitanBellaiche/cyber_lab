# zoobar/bank.py
from zoodb import bank_setup, transfer_setup, Bank, Transfer
from debug import *
import time
from sqlalchemy import or_

# פונקציה פנימית – לוודא שיש למשתמש רשומה בטבלת Bank
def _get_or_create_account(db, username):
    acc = db.query(Bank).get(username)
    if acc is None:
        acc = Bank()
        acc.username = username
        acc.zoobars = 10   # התחלה עם 10 זובר
        db.add(acc)
        db.commit()
    return acc


def transfer(sender, recipient, zoobars):
    db = bank_setup()

    # מבטיח שיש רשומות בנק לשני הצדדים
    sender_acc    = _get_or_create_account(db, sender)
    recipient_acc = _get_or_create_account(db, recipient)

    if zoobars < 0:
        raise ValueError("Negative transfer not allowed")

    if sender_acc.zoobars < zoobars:
        raise ValueError("Not enough zoobars")

    sender_acc.zoobars    -= zoobars
    recipient_acc.zoobars += zoobars

    db.commit()

    # לוג העברה – בטבלת Transfer (ב-db/transfer)
    tdb = transfer_setup()
    t = Transfer()
    t.sender    = sender
    t.recipient = recipient
    t.amount    = zoobars
    t.time      = time.asctime()
    tdb.add(t)
    tdb.commit()


def balance(username):
    db = bank_setup()
    acc = _get_or_create_account(db, username)
    return acc.zoobars


def get_log(username):
    tdb = transfer_setup()
    l = tdb.query(Transfer).filter(
        or_(Transfer.sender == username,
            Transfer.recipient == username)
    )
    r = []
    for t in l:
        r.append({
            'time': t.time,
            'sender': t.sender,
            'recipient': t.recipient,
            'amount': t.amount,
        })
    return r
