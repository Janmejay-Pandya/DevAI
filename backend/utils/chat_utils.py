from asgiref.sync import sync_to_async
from chat.models import Message


class ChatUtil:
    _websocket = None

    @classmethod
    def set_websocket(cls, websocket):
        cls._websocket = websocket

    @classmethod
    def clear_websocket(cls):
        cls._websocket = None

    @classmethod
    async def send_message(
        cls, chat_id, response_text, is_seeking_approval, project_stage
    ):
        if not cls._websocket:
            print("Websocket not found!")
            return

        message_content = {
            "response": response_text,
            "is_seeking_approval": is_seeking_approval,
            "project_stage": project_stage,
        }
        await sync_to_async(Message.objects.create)(
            chat=chat_id,
            sender="assistant",
            content=response_text
        )
        await cls._websocket.send_json(message_content)
