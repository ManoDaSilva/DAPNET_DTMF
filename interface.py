import json
import pprint
import websocket
from websocket import create_connection
import socket
import serial
import time
import json
import os
from urllib.request import urlopen

##Canned messages, numbered from 0 to 89
cannedMsg = [
    "Test de Couverture",
    "R0 B-EARS. RDV sur Relais ou 145.500MHz",
    "Canned msg 2",
    "Canned msg 3",
    "Canned msg 4",
    "Canned msg 5",
]

##For fast RIC dialing, if you type 0, it'll default to this one.
defaultRic = 2065009

#Initialize the serial port, edit if using another one...
ser = serial.Serial(
    "/dev/ttyACM0",
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=None,
)

## Barely modified from Unipager-SendWebsocket. Sends a websocket request to unipager with specified RIC, type, text, function
def sendToUnipager(ric, text, m_type, m_func):
    time.sleep(2)
    websocket.enableTrace(True)
    ws = create_connection("ws://localhost:8055/")
    string_to_send = (
        '{"SendMessage": {"addr": %s, "data": "%s", "mtype": "%s", "func": "%s"}}'
        % (ric, text, m_type, m_func)
    )
    ws.send(string_to_send)

#Gets the CPU load and IP Address, and returns a string ready to send to unipager
def sendSysStatus():
    hostname = socket.gethostname()
    ipAddress = socket.gethostbyname(hostname)
    rawCpuTemp = 0
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        rawCpuTemp = f.read()
    cpuTemp = int(rawCpuTemp) / 1000
    sysInfo = "CPU Temp: {} C, IP Addr: {}".format(cpuTemp, ipAddress)
    return sysInfo

#Same as above, but with unipager status
def sendUnipagerStatus():
    # We parse the config file to get the transmitter's callsign
    f = open('/var/lib/unipager/config.json')
    data = json.load(f)
    callsign = data['master']['call']
    f.close()
    #From https://hampager.de/dokuwiki/doku.php?id=queueunipager - we poll the connection status and server used
    response = urlopen("http://127.0.0.1:8073/status")
    data = json.loads(response.read())
    if data['connected'] == True:
        status = "Connected"
    else:
        status = "Disconnected"
    server = data['master']
    unipagerInfo = "Callsign: {}, Server: {}, Status: {}".format(callsign, server, status)
    return unipagerInfo

#Does what's written on the tin: restarts the Unipager Service
def restartUnipager():
    os.system("sudo service unipager restart")
    #Let's give it some time to restart the service
    time.sleep(5)
    return "Unipager Restart Successful"

#Runs continuously. Waits for the "#" sign to end line, decodes it then sees what's in there.
while True:
    data = ""
    dataRaw = ser.read_until(b"\x23")
    print(str(dataRaw))
    dataUTF = dataRaw.decode("utf-8")
    dataUTF = dataUTF[:-1]
    dataProcessed = dataUTF.split("*", 2)
    print(dataProcessed)
    #Sanity check. We need two inputs, not more not less
    if len(dataProcessed) == 2:
        #Catch any empty fields that would make the script crash when parsing it to an int
        try:
            msgIndex = int(dataProcessed[1])
            #If the specified RIC is 0, then set it to the default RIC
            if dataProcessed[0] == "0":
                ric = defaultRic
            else:
                ric = dataProcessed[0]
                
            #Default behavior: send a canned message to unipager
            if 0 <= msgIndex < len(cannedMsg):
                sendToUnipager(ric, cannedMsg[msgIndex], "AlphaNum", "Func3")
            #Additional features
            elif msgIndex == 99:
                sendToUnipager(ric, sendSysStatus(), "AlphaNum", "Func3")
            elif msgIndex == 98:
                sendToUnipager(ric, sendUnipagerStatus(), "AlphaNum", "Func3")
            elif msgIndex == 97:
                sendToUnipager(ric, restartUnipager(), "AlphaNum", "Func3")
            else:
                print("Invalid msg index or RIC range")
        except:
            print("Invalid or empty fields")

    else:
        print("Incorrect message length")
