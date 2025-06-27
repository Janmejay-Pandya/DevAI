import json
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from agents.master_agent import MasterAgent
from projects.models import Project
from utils.terminal_utils import TerminalLogger
from utils.chat_utils import ChatUtil


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        await self.accept()
        ChatUtil.set_websocket(self)
        await TerminalLogger.log({
            "info", "Setup", f"Connected to chat {self.chat_id}"})

    async def disconnect(self, close_code):
        ChatUtil.clear_websocket()


    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("content", "")

        master_agent = MasterAgent(self.chat_id)
        chat = get_object_or_404(Chat, id=self.chat_id, user=self.scope["user"])
        project_stage = Project.objects.get(chat=chat).current_step

        response_text, is_seeking_approval = master_agent.handle_input(
            user_message
        )

        self.send_json({"response": response_text, "is_seeking_approval": is_seeking_approval, "project_stage": project_stage})

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))



from channels.generic.websocket import AsyncWebsocketConsumer
from utils.terminal_utils import TerminalLogger

class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        TerminalLogger.set_websocket(self)
        await TerminalLogger.log("success", "Setup", "Connection Established!")

    async def disconnect(self, close_code):
        TerminalLogger.clear_websocket()
