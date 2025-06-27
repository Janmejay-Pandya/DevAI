import json
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from agents.master_agent import MasterAgent
from projects.models import Project

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": f"Connected to chat {self.chat_id}"
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("content", "")

        master_agent = MasterAgent(self.chat_id)
        chat = get_object_or_404(Chat, id=self.chat_id, user=None)
        project_stage = Project.objects.get(chat=chat).current_step

        response_text, is_seeking_approval = master_agent.handle_input(
            user_message
        )

        self.send_json({"response": response_text, "is_seeking_approval": is_seeking_approval, "project_stage": project_stage})

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))
