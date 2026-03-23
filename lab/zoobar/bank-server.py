#!/usr/bin/env python3
import sys
from rpclib import RpcServer
import bank
import auth_client as auth   # כדי לוודא את ה-token

class BankRpcServer(RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars, token):
        # לוג קטן לשרט:
        print(f"[BANK-SERVER] transfer {zoobars} from {sender} to {recipient}")

        # אימות ה-token מול שירות האימות
        if not auth.check_token(sender, token):
            print("[BANK-SERVER] invalid token for", sender, "– aborting transfer")
            # נחזיר False כדי שהקליינט ידע שזה נכשל
            return False

        # אם ה-token תקין – נבצע את ההעברה עצמה (לוגיקה טהורה של בנק)
        bank.transfer(sender, recipient, zoobars)
        return True

    def rpc_balance(self, username):
        print(f"[BANK-SERVER] balance check for {username}")
        return bank.balance(username)

    def rpc_get_log(self, username):
        print(f"[BANK-SERVER] get_log for {username}")
        return bank.get_log(username)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: bank-server.py <dummy> <sockpath>")
        sys.exit(1)

    sockpath = sys.argv[2]
    s = BankRpcServer()
    s.run_sockpath_fork(sockpath)
