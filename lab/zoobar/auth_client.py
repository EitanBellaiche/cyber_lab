from debug import *
from zoodb import *
import rpclib

SOCKPATH = "/authsvc/sock"

def login(username, password):
    c = rpclib.client_connect(SOCKPATH)
    rv = c.call("login", username=username, password=password)
    c.close()
    return rv

def register(username, password):
    c = rpclib.client_connect(SOCKPATH)
    rv = c.call("register", username=username, password=password)
    c.close()
    return rv

def check_token(username, token):
    c = rpclib.client_connect(SOCKPATH)
    rv = c.call("check_token", username=username, token=token)
    c.close()
    return rv
