#!/usr/bin/env python2

import rpclib
import sys
import auth

class AuthRpcServer(rpclib.RpcServer):

    def rpc_login(self, username, password):
        # כאן אפשר להדפיס אם אתה רוצה debug, אבל dbg לא חובה
        # print("auth-server: login", username)
        return auth.login(username, password)

    def rpc_register(self, username, password):
        # print("auth-server: register", username)
        return auth.register(username, password)

    def rpc_check_token(self, username, token):
        # print("auth-server: check_token", username)
        return auth.check_token(username, token)

(_, dummy_zookld_fd, sockpath) = sys.argv

s = AuthRpcServer()
s.run_sockpath_fork(sockpath)
