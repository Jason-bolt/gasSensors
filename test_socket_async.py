import network
import socket
import gc
import uasyncio as asyncio

gc.collect()

ssid="My-access-point"
password = "12345"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
    pass

print("Connection successful")
print(ap.ifconfig())

def web_page():
    html = """
            <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                    <h1>Hello World!</h1>
                </body>
            </html>
"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

async def connect():
    conn, addr = await s.accept()
    print('Got a connection from %s' %str(addr))
    
    request = conn.recv(1024)
    print('Content = %s' % str(request))
    response = web_page()
    conn.send(response)
    conn.close()
    
async def foo():
    print("1")
    print("2")
    await asyncio.sleep(1)
    
async def main():
    while True:
        task = asyncio.create_task(connect())
        task1 = asyncio.create_task(foo())
    await task1

asyncio.run(main())
    

