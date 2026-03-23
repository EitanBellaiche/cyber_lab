#!/usr/bin/env python3
import sys
from rpclib import RpcServer
import bank
import auth_client as auth   

class BankRpcServer(RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars, token):

        print(f"[BANK-SERVER] transfer {zoobars} from {sender} to {recipient}")

        if not auth.check_token(sender, token):
            print("[BANK-SERVER] invalid token for", sender, "– aborting transfer")

            return False

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
