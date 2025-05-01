from channels.generic.websocket import AsyncWebsocketConsumer
from utils.terminal_utils import TerminalLogger

class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        TerminalLogger.set_websocket(self)
        await TerminalLogger.log("success", "Setup", "Connection Established!")

    async def disconnect(self, close_code):
        TerminalLogger.clear_websocket()