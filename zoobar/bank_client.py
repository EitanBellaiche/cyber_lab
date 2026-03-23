from rpclib import client_connect

SOCKPATH = "/banksvc/sock"

def transfer(sender, recipient, zoobars, token):
    c = client_connect(SOCKPATH)
    return c.call("transfer",
                  sender=sender,
                  recipient=recipient,
                  zoobars=zoobars,
                  token=token)

def balance(username):
    c = client_connect(SOCKPATH)
    return c.call("balance", username=username)

def get_log(username):
    c = client_connect(SOCKPATH)
    return c.call("get_log", username=username)
