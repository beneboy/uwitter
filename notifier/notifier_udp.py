import json
import socket


def recv_json_message(conn):
    raw_message = conn.recv(1024)
    length = int(raw_message[:4])

    message = json.loads(raw_message[4:length+4])
    return message

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', 5004))
    while True:
        # single threaded for simplicity
        message = recv_json_message(server_socket)
        print message

if __name__ == '__main__':
    run_server()
