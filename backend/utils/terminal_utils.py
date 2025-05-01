import json
from datetime import datetime
import asyncio

class TerminalLogger:
    _websocket = None

    @classmethod
    def set_websocket(cls, websocket):
        cls._websocket = websocket

    @classmethod
    def clear_websocket(cls):
        cls._websocket = None

    @classmethod
    async def log(cls, log_type, category, message):
        if not cls._websocket:
            print(f"[{category.upper()}] ({log_type.upper()}) {message}")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "time": now,
            "type": log_type,
            "category": category,
            "message": message,
        }
        await cls._websocket.send(text_data=json.dumps(payload))
