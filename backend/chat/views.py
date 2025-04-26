from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, UserSerializer
from django.contrib.auth.models import User
from agents.master_agent import MasterAgent

# # for testing!!!! must remove later!!!!!
# from rest_framework.decorators import authentication_classes, permission_classes

# @authentication_classes([]) # for testing!!!! must remove later!!!!!
# @permission_classes([]) # for testing!!!! must remove later!!!!!


class CreateListUserView(generics.ListCreateAPIView):
    # specifies the list of objects we need to check to not create preexisting user
    queryset = User.objects.all()
    # tells the data what kind of data we need to accept
    serializer_class = UserSerializer
    # who can access
    permission_classes = [AllowAny]
    def get_queryset(self):
        return User.objects.all()

class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        chat_pk = self.kwargs.get('chat_pk')
        return Message.objects.filter(chat_id=chat_pk, chat__user=self.request.user)
    
    def perform_create(self, serializer):
        chat_pk = self.kwargs.get('chat_pk')
        chat = get_object_or_404(Chat, id=chat_pk, user=self.request.user)
        serializer.save(chat=chat)

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        chat_pk = self.kwargs.get('chat_pk')
        return Message.objects.filter(chat_id=chat_pk, chat__user=self.request.user)

class AssistantResponseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        chat_id = request.data.get('chat_id')
        user_message = request.data.get('message')
        is_choice = request.data.get('is_choice')
        
        chat = get_object_or_404(Chat, id=chat_id, user=request.user)
        # echoing for now, will add agent response here
        # response_text = f"You said: {user_message}"

        master_agent = MasterAgent(chat_id)
        response_text, is_seeking_approval = master_agent.handle_input(user_message, is_choice)
        
        Message.objects.create(
            chat=chat,
            sender='assistant',
            content=response_text
        )
        
        return Response({
            'response': response_text,
            'is_seeking_approval': is_seeking_approval
        }, status=status.HTTP_200_OK)