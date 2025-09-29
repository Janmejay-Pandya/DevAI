import json
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from agents.new_master_agent import MasterAgent
from projects.models import Project
from utils.terminal_utils import TerminalLogger
from utils.chat_utils import ChatUtil


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        await self.accept()
        print("connected")
        ChatUtil.set_websocket(self)
        await TerminalLogger.log("info", "Setup", f"Connected to chat {self.chat_id}")

    async def disconnect(self, close_code):
        ChatUtil.clear_websocket()

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("content", "")

        master_agent = await get_master_agent(self.chat_id)
        # chat = await get_chat(self.chat_id, self.scope["user"])
        # project_stage = Project.objects.get(chat=chat).current_step
        await master_agent.handle_input(user_message)

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))


@sync_to_async
def get_chat(chat_id, user):
    return get_object_or_404(Chat, id=chat_id, user=user)


@sync_to_async
def get_master_agent(chat_id):
    return MasterAgent(chat_id)
