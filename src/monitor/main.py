import time
import os, threading

from src.monitor.check import check_data


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept()
        print(f'[*] Acceped connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(
            target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'Hello')


if __name__ == '__main__':
    t = threading.Thread(target=main, name='test')
    t.start()

    t.join()
    print(threading.currentThread().name)