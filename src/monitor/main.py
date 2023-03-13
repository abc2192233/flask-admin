import socket
import sqlite3
import time
import threading

IP = '127.0.0.1'
PORT = 12345


def main():
    pass


def collect_data():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(
            target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'Hello')


if __name__ == '__main__':
    conn = sqlite3.connect('../demo01/sample_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alert_strategy")
    alert_strategy = cursor.fetchall()

    cursor.execute("SELECT * FROM vol_file")
    light_strategy = cursor.fetchall()

    conn.close()

    print(alert_strategy, light_strategy)
