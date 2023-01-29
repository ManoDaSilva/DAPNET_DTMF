import json
import pprint
import websocket
from websocket import create_connection

import serial
import io
import time

cannedMsg = ["Test de Couverture","R0 B-EARS. RDV sur Relais ou 145.500MHz","Canned msg 2", "Canned msg 3", "Canned msg 4", "Canned msg 5"]


def sendToUnipager(ric, text, m_type, m_func):
    websocket.enableTrace(True)
    ws = create_connection('ws://localhost:8055/')
    string_to_send = "{\"SendMessage\": {\"addr\": %s, \"data\": \"%s\", \"mtype\": \"%s\", \"func\": \"%s\"}}" % (ric, text, m_type, m_func)
    ws.send(string_to_send)
    
ser = serial.Serial('/dev/ttyACM0',
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=None)

while True:
    data = ""
    dataRaw = ser.read_until(b'\x23')
    print(str(dataRaw))
    dataUTF = dataRaw.decode('utf-8')
    dataUTF = dataUTF[:-1]
    dataProcessed = dataUTF.split("*",2)
    print(dataProcessed)
    if len(dataProcessed) == 2:
        time.sleep(2)
        try:
            msgIndex = int(dataProcessed[1])
                if 0 <= msgIndex < len(cannedMsg):
                sendToUnipager(dataProcessed[0],cannedMsg[msgIndex],"AlphaNum","Func3")
        except:
            print("Invalid or empty fields")
        else:
            print("Invalid msg index or RIC range")
    else:
        print("Incorrect MSG lenght")