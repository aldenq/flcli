#        further-link command line interface
# will attempt to run the given python file at the provided destination using further-link
#examples:
# python3.8 flcli.py 127.0.0.1 helloworld.py
# python3.8 flcli.py 192.168.0.1 helloworld.py




import requests
import websockets
import asyncio
import ssl
import json
import sys
import subprocess
import fileinput

if len(sys.argv) == 1:
    print("further-link command line interface\nexample:\n   python3.8 flcli.py 192.168.0.1 helloworld.py\nadditional info can by found on the github at https://github.com/aldenq/flcli")
    exit()

ip = sys.argv[1].replace("-",".") #string replace is just to accommodate ip's in the format of a-b-c-d and a.b.c.d
file = sys.argv[2]


flink_port = "8028"

websurl = "wss://" + ip + ":" + flink_port
#.further-link.pi-top.com
    

        
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

def fl_format(m_type,m_data): #format stuff into further link format
    output = {}
    output["type"] = m_type
    output["data"] = m_data
    formatted = json.dumps(output)
    #print(formatted)
    return(formatted)


#clr = get_stdin()
async def send_and_run(): #takes python file and sends it over for the pi-top to execute, during executing listens for stdouts and prints them to screen
    ssl_context = ssl.SSLContext() #not secure
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    uri = websurl + "/run-py"
    #fl_format("stdin","test123")
    async with websockets.connect(uri,ssl=ssl_context) as websocket:
        await websocket.send(code)
        
        while True:
            data = await websocket.recv()
            m_type,m_data = parse_message(data)
            
            if m_type == "stdout" or m_type == "stderr": 
                print(m_data["output"])
            
            if m_type == "error" or m_type == "stopped" or m_type == "stderr": #continue to recieve data until either the process crashes or stops
                print(m_type)
                break
asyncio.get_event_loop().run_until_complete(send_and_run())


