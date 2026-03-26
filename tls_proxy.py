#!/usr/bin/env python3
import socket
import ssl
import sys
import threading


BUFFER_SIZE = 65536


def read_request(conn):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            return None
        data += chunk

    header_blob, body = data.split(b"\r\n\r\n", 1)
    lines = header_blob.split(b"\r\n")
    request_line = lines[0]

    headers = []
    content_length = 0
    host_header = None
    for raw_line in lines[1:]:
        if b":" not in raw_line:
            continue
        name, value = raw_line.split(b":", 1)
        lower_name = name.strip().lower()
        value = value.strip()

        if lower_name == b"content-length":
            content_length = int(value.decode("ascii", "ignore") or "0")
        elif lower_name == b"host":
            host_header = value.decode("ascii", "ignore")

        if lower_name in {
            b"connection",
            b"proxy-connection",
            b"keep-alive",
            b"x-forwarded-proto",
            b"x-forwarded-host",
            b"x-forwarded-port",
        }:
            continue

        headers.append((name.decode("ascii", "ignore"), value.decode("latin-1", "ignore")))

    while len(body) < content_length:
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        body += chunk

    return request_line, headers, host_header, body


def build_request(request_line, headers, host_header, body, listen_port):
    forwarded = [request_line]
    for name, value in headers:
        forwarded.append(f"{name}: {value}".encode("latin-1"))

    if host_header:
        forwarded.append(f"X-Forwarded-Host: {host_header}".encode("latin-1"))
    forwarded.append(b"X-Forwarded-Proto: https")
    forwarded.append(f"X-Forwarded-Port: {listen_port}".encode("ascii"))
    forwarded.append(b"Connection: close")
    forwarded.append(b"")
    return b"\r\n".join(forwarded) + b"\r\n" + body


def proxy_connection(client_conn, backend_host, backend_port, listen_port):
    backend = None
    try:
        req = read_request(client_conn)
        if req is None:
            return

        request_line, headers, host_header, body = req
        backend = socket.create_connection((backend_host, backend_port))
        backend.sendall(build_request(request_line, headers, host_header, body, listen_port))

        while True:
            chunk = backend.recv(BUFFER_SIZE)
            if not chunk:
                break
            client_conn.sendall(chunk)
    finally:
        if backend is not None:
            backend.close()
        client_conn.close()


def serve_forever(listen_port, backend_host, backend_port, certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", listen_port))
    server.listen(5)

    while True:
        conn, _addr = server.accept()
        try:
            tls_conn = context.wrap_socket(conn, server_side=True)
        except ssl.SSLError:
            conn.close()
            continue

        thread = threading.Thread(
            target=proxy_connection,
            args=(tls_conn, backend_host, backend_port, listen_port),
            daemon=True,
        )
        thread.start()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: tls_proxy.py <listen_port> <backend_host> <backend_port> <certfile> <keyfile>")
        sys.exit(1)

    serve_forever(
        int(sys.argv[1]),
        sys.argv[2],
        int(sys.argv[3]),
        sys.argv[4],
        sys.argv[5],
    )
