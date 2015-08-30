import json
import socket
from db import process_request_message


def get_message_length(conn):
    length_bytes = conn.recv(4)
    return int(length_bytes)


def recv_json_message(conn):
    message_length = get_message_length(conn)
    json_message = ''
    while len(json_message) < message_length:
        json_message += conn.recv(message_length - len(json_message))

    message = json.loads(json_message)
    return message


def send_json_message(conn, message):
    if message:
        message_json = json.dumps(message)
    else:
        message_json = ''

    conn.sendall('{:04}'.format(len(message_json)))
    # 4 bytes for the length of the data, hopefully less than 9999 chars. keeping it simple with ascii and JSON
    if message_json:
        conn.sendall(message_json)
        

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5002))
    server_socket.listen(5)
    while True:
        # single threaded for simplicity
        conn, addr = server_socket.accept()
        message = recv_json_message(conn)
        response = process_request_message(message)
        send_json_message(conn, response)


if __name__ == '__main__':
    run_server()
