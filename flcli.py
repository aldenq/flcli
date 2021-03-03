#        further-link command line interface
# will attempt to run the given python file at the provided destination using further-link
#examples:
# python3.8 flcli.py 127.0.0.1 helloworld.py
# python3.8 flcli.py 192.168.0.1 helloworld.py


# -c flag can be used to show get syntax errors
# python3.8 flcli.py 192.168.0.1 helloworld.py -c




import requests
import websockets
import asyncio
import ssl
import json
import sys
import subprocess



    

ip = sys.argv[1].replace(".","-") #string replace is just to accommodate ip's in the format of a-b-c-d and a.b.c.d
file = sys.argv[2]


if len(sys.argv) ==4:
    flag = sys.argv[3]
else:
    flag = False
    
if flag == "-c":
    subprocess.run(["python3.8" ,"-m","py_compile",file])


    
flink_port = "8028"

URL = "https://" + ip + ".further-link.pi-top.com:" +flink_port+ "/status"
websurl = "wss://" + ip + ".further-link.pi-top.com:" + flink_port


def check_online(): #check if target pi-top is online
    r = requests.get(url = URL)  
    data = r.text
    if data == "OK":
        print("device found")
    else:
        print("pi-top cannot be connected to")
        exit()
        
def get_code(file): #retrieves code from specified file and formats it to be sent
    f = open(file, "r")
    code = f.read()
    code=code.replace("\n","\\n") #escape some chars to avoid screwing with format
    code=code.replace("\"","\\\"")
    return("""{"type":"start","data":{"sourceScript":\""""+code+"""\"}}""")

code = get_code(file)

def parse_message(message): #function borrowed from further-link(/usr/lib/pt-further-link/src/message.py) source, parses message from furtherlink format
    try:
        msg = json.loads(message)
    except json.decoder.JSONDecodeError:
        raise BadMessage()

    msg_type = msg.get('type')
    msg_data = msg.get('data')

    msg_type = msg_type if isinstance(msg_type, str) else ''
    msg_data = msg_data if isinstance(msg_data, dict) else {}

    return msg_type, msg_data


async def send_and_run(): #takes python file and sends it over for the pi-top to execute, during executing listens for stdouts and prints them to screen
    ssl_context = ssl.SSLContext() #not secure
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    uri = websurl + "/run-py"
    
    async with websockets.connect(uri,ssl=ssl_context) as websocket:
        await websocket.send(code)
        
        while True:
            data = await websocket.recv()
            m_type,m_data = parse_message(data) 
            
            if m_type == "stdout": 
                print(m_data["output"])
            if m_type == "error" or m_type == "stopped": #continue to recieve data until either the process crashes or stops
                print(m_type)
                break
check_online()
asyncio.get_event_loop().run_until_complete(send_and_run())


