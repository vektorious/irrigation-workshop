import wifi
import uasyncio as asyncio
import machine
import time
import ubinascii
import hashlib
import ustruct

IP = wifi.connect("SSID", "pwd")
moisture_sensor = machine.ADC(26)

def load_html():
    with open('index.html', 'r') as f:
        return f.read()

html_content = load_html()

async def serve_client(reader, writer):
    try:
        request_line = await reader.readline()
        print('Request:', request_line)

        headers = {}
        while True:
            line = await reader.readline()
            if line == b"\r\n":
                break
            if b":" in line:
                key, value = line.decode().split(":", 1)
                headers[key.strip()] = value.strip()

        # Upgrade requested?
        if headers.get("Upgrade", "").lower() == "websocket":
            print('WebSocket upgrade requested')
            websocket_key = headers["Sec-WebSocket-Key"]
            GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
            accept = ubinascii.b2a_base64(hashlib.sha1((websocket_key + GUID).encode()).digest()).decode().strip()

            await writer.awrite(
                'HTTP/1.1 101 Switching Protocols\r\n'
                'Upgrade: websocket\r\n'
                'Connection: Upgrade\r\n'
                'Sec-WebSocket-Accept: {}\r\n\r\n'.format(accept)
            )

            print('WebSocket connection established.')

            while True:
                moisture = moisture_sensor.read_u16() / 65535 * 100
                message = '{"moisture": %.2f}' % moisture
                await send_ws_message(writer, message)
                await asyncio.sleep(2)
        else:
            # Normal HTTP request
            print('Serving index.html')
            response = 'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n' + html_content
            await writer.awrite(response)
            await writer.aclose()
    except Exception as e:
        print('Error in serve_client:', e)
        await writer.aclose()

async def send_ws_message(writer, message):
    frame = bytearray()
    frame.append(0x81)  # FIN and Text Frame opcode
    length = len(message)
    if length < 126:
        frame.append(length)
    else:
        frame.append(126)
        frame.extend(ustruct.pack(">H", length))
    frame.extend(message.encode('utf-8'))
    await writer.awrite(frame)

async def main():
    server = await asyncio.start_server(serve_client, "0.0.0.0", 80)
    print('Server started at IP', IP)
    await server.wait_closed()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Server stopped')

