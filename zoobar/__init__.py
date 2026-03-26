#!/usr/bin/env python3

# For relative imports to work in Python 3.6
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask, g, redirect, request

import login
import index
import users
import transfer
import zoobarjs
import zoodb
from debug import catch_err
from login import set_csrf_cookie

app = Flask(__name__)


def request_is_secure():
    return (request.headers.get("X-Forwarded-Proto") == "https" or
            request.environ.get("wsgi.url_scheme") == "https")


def https_redirect_url():
    host = request.host.split(":", 1)[0]
    port = os.environ.get("ZOOBAR_TLS_PORT", "8443")
    target = request.full_path
    if target.endswith("?"):
        target = target[:-1]
    return "https://%s:%s%s" % (host, port, target)

app.add_url_rule("/", "index", index.index, methods=['GET', 'POST'])
app.add_url_rule("/users", "users", users.users)
app.add_url_rule("/transfer", "transfer", transfer.transfer, methods=['GET', 'POST'])
app.add_url_rule("/zoobarjs", "zoobarjs", zoobarjs.zoobarjs, methods=['GET'])
app.add_url_rule("/login", "login", login.login, methods=['GET', 'POST'])
app.add_url_rule("/logout", "logout", login.logout)


@app.before_request
@catch_err
def enforce_https():
    if os.environ.get("ZOOBAR_REQUIRE_TLS") == "1" and not request_is_secure():
        return redirect(https_redirect_url(), code=302)

@app.after_request
@catch_err
def disable_xss_protection(response):
    response.headers.add("X-XSS-Protection", "0")
    if request_is_secure():
        response.headers.add("Strict-Transport-Security", "max-age=86400")
    set_csrf_cookie(response)
    return response

if __name__ == "__main__":
    app.run()
