import array
import datetime
import io
import socket
import sqlite3
import time
import threading
from multiprocessing.managers import BaseManager
from typing import Dict
from multiprocessing import Queue

from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from pydub import AudioSegment
from pydub.playback import play

IP = '127.0.0.1'
PORT = 12345
lock = threading.Lock()
vol_flag = 0
model_id = 'damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k'
sambert_hifigan_tts = pipeline(task=Tasks.text_to_speech, model=model_id)


def check_message(config: Dict, message: Dict):
    global vol_flag
    for strategy in config['alert_strategy']:
        if int(strategy[2]) < int(message['b']) < int(strategy[3]):
            print(datetime.datetime.now())
            print(strategy)
            for x in config['vol_file']:
                if x[0] == strategy[4]:
                    if vol_flag == 0:
                        alert_thread = threading.Thread(target=send_alert, args=(x, message))
                        alert_thread.start()
                        # send_alert(x, message)
                    else:
                        print('device busy')


def send_alert(vol_array: array, message: Dict):
    print(vol_array)
    global vol_flag
    vol_flag = 1
    global sambert_hifigan_tts

    if vol_array[2] == 'context':
        output = sambert_hifigan_tts(input=message['a'] + vol_array[3])
        wav = output[OutputKeys.OUTPUT_WAV]
        song = AudioSegment.from_file(io.BytesIO(wav), format="wav")
        play(song)
        print(vol_array[3])

    if vol_array[2] == 'file':

        output = sambert_hifigan_tts(input=message['a'])
        wav = output[OutputKeys.OUTPUT_WAV]
        song = AudioSegment.from_file(io.BytesIO(wav), format="wav")
        play(song)
        song = AudioSegment.from_file(f'../demo01/files/{vol_array[4]}', format="wav")
        play(song)
        print(vol_array[4])

    vol_flag = 0


def main():
    pass


def collect_data(info_queue: Queue):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(
            target=handle_client, args=(client, info_queue))
        client_handler.start()


def handle_client(client_socket, queue):
    with client_socket as sock:
        request = sock.recv(10 * 1024)
        queue.put(request.decode("utf-8"))
        # print(f'[*] Received: {request.decode("utf-8")}')
        # sock.send(b'Hello')


def load_config() -> Dict:
    lock.acquire()
    config = dict()
    conn = sqlite3.connect('../demo01/sample_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alert_strategy")
    alert_strategy = cursor.fetchall()
    config['alert_strategy'] = alert_strategy

    cursor.execute("SELECT * FROM vol_file")
    light_strategy = cursor.fetchall()
    config['vol_file'] = light_strategy

    conn.close()
    lock.release()

    return config


if __name__ == '__main__':
    info_queue = Queue()

    config = load_config()
    collect_thread = threading.Thread(target=collect_data, args=(info_queue,))
    collect_thread.start()
    while True:
        message = eval(info_queue.get(True))
        check_message(config, message)
