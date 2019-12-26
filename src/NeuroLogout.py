import socket
import json
import time


def disconnect(sensor):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 1234))

    client.send(json.dumps({
        'instruction': 'disconnect',
        'bluetoothName': sensor
    }))
    
    time.sleep(2)
    client.close()
