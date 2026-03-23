from flask import g, render_template, request

from login import requirelogin
from zoodb import *
from debug import *
import bank_client as bank
import traceback

@catch_err
@requirelogin
def transfer():
    warning = None
    try:
        if 'recipient' in request.form:
            zoobars_str = request.form['zoobars']
            zoobars = int(zoobars_str)  # המרה למספר

            bank.transfer(
                g.user.person.username,
                request.form['recipient'],
                zoobars,
                g.user.token,          # <<< שולחים token
            )
            warning = "Sent %d zoobars" % zoobars

    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form.get('recipient', '(unknown)')

    return render_template('transfer.html', warning=warning)
