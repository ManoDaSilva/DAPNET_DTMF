import json
import pprint
import websocket
from websocket import create_connection
import socket
import serial
import time
import json
from urllib.request import urlopen


cannedMsg = [
    "Test de Couverture",
    "R0 B-EARS. RDV sur Relais ou 145.500MHz",
    "Canned msg 2",
    "Canned msg 3",
    "Canned msg 4",
    "Canned msg 5",
]
def sendToUnipager(ric, text, m_type, m_func):
    time.sleep(2)
    websocket.enableTrace(True)
    ws = create_connection("ws://localhost:8055/")
    string_to_send = (
        '{"SendMessage": {"addr": %s, "data": "%s", "mtype": "%s", "func": "%s"}}'
        % (ric, text, m_type, m_func)
    )
    ws.send(string_to_send)


def sendSysStatus():
    hostname = socket.gethostname()
    ## getting the IP address using socket.gethostbyname() method
    ipAddress = socket.gethostbyname(hostname)
    rawCpuTemp = 0
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        rawCpuTemp = f.read()
    cpuTemp = int(rawCpuTemp) / 1000
    sysInfo = "CPU Temp: {} C, IP Addr: {}".format(cpuTemp, ipAddress)
    return sysInfo
    
def sendUnipagerStatus():
    # Opening JSON file
    f = open('/var/lib/unipager/config.json')
    data = json.load(f)
    callsign = data['master']['call']
    f.close()
    
    response = urlopen("http://127.0.0.1:8073/status")
    data = json.loads(response.read())
    if data['connected'] == True:
        status = "Connected"
    else:
        status = "Disconnected"
    server = data['master']
    unipagerInfo = "Callsign: {}, Server: {}, Status: {}".format(callsign, server, status)
    return unipagerInfo


ser = serial.Serial(
    "/dev/ttyACM0",
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=None,
)

while True:
    data = ""
    dataRaw = ser.read_until(b"\x23")
    print(str(dataRaw))
    dataUTF = dataRaw.decode("utf-8")
    dataUTF = dataUTF[:-1]
    dataProcessed = dataUTF.split("*", 2)
    print(dataProcessed)
    if len(dataProcessed) == 2:
        try:
            msgIndex = int(dataProcessed[1])
            if 0 <= msgIndex < len(cannedMsg):
                sendToUnipager(
                    dataProcessed[0], cannedMsg[msgIndex], "AlphaNum", "Func3"
                )
            elif msgIndex == 99:
                sendToUnipager(dataProcessed[0], sendSysStatus(), "AlphaNum", "Func3")
            elif msgIndex == 98:
                sendToUnipager(dataProcessed[0], sendUnipagerStatus(), "AlphaNum", "Func3")
            else:
                print("Invalid msg index or RIC range")
        except:
            print("Invalid or empty fields")

    else:
        print("Incorrect message length")
