class ChatUtil:
    _websocket = None

    @classmethod
    def set_websocket(cls, websocket):
        cls._websocket = websocket

    @classmethod
    def clear_websocket(cls):
        cls._websocket = None

    @classmethod
    async def send_message(cls, message_content):
        if not cls._websocket:
            print("Websocket not found!")
            return

        await cls._websocket.send_json(message_content)
