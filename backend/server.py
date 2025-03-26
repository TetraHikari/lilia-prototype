import asyncio
import websockets
import json
import paho.mqtt.publish as publish

connected_clients = set()

async def handler(websocket):
    print("Client connected")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            print("📨 Received:", message)
            try:
                data = json.loads(message)

                # From frontend: control command
                if data.get("type") == "command":
                    publish.single("esp32/control", payload=data["value"], hostname="localhost")
                else:
                    # From Pi: forward sensor data to all browsers
                    for client in connected_clients:
                        if client != websocket:
                            await client.send(message)

            except Exception as e:
                print("❌ JSON parse error:", e)

    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("✅ WS server running on ws://0.0.0.0:8765")
        await asyncio.Future()

asyncio.run(main())
