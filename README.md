# DAPNET_DTMF
Allows to locally use a Unipager/DAPNET transmitter, through DTMF tones, even without an internet/hamnet connection. 

# System Structure
This is added on top of an existing unipager POCSAG audio transmitter. On the Rx path, a MT8870 is connected, which decodes DTMF tones. 
An additional Arduino takes care of translating this logic into Serial, and spits the decoded digits to the Raspberry Pi running unipager. 
A small python script then takes this info and transmits canned messages to unipager via a Websocket connection

# Features
You can send messages via DTMF by dialing:
```
#Ric*MessageNr#
```
You can set up to 90 canned messages. 91 to 99 have been blocked for "special" messages. So far, those have been implemented:
* 98: Unipager status (server, callsign, connection status)
* 99: System status (CPU temp, IP Address)


# Getting started

## Arduino
No additional libraries are required. Just wire the MT8870 as explained on the sketch, upload it and you're good to go. Confirm consistent DTMF decoding with the serial monitor.
Connect the Arduino via USB to the Rpi, or directly through the GPIO (be careful about the logic levels!).

## Raspberry Pi
Install unipager and set it up the classic way.

Install pip and git:
```bash
sudo apt install git pip
```
Install required python modules:
```bash
sudo pip install websocket-client pyserial
```
Edit interface.py and change the serial interface if needed (by default: first USB serial adapter). If you're using directly the GPIO UART, you might need to disable the serial console or others, I haven't looked it up just yet.	
Edit the canned messages as your heart desires.
	
Start the script, it should now be ready to receive DTMF calls.


# Credits
* https://github.com/dk4pa/UniPager-SendWebsocket
* https://electropeak.com/learn/interfacing-mt8870-dtmf-decoder-module-with-arduino/