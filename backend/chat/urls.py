from django.urls import path
from . import views

urlpatterns = [
    # Chat endpoints
    path("chats/", views.ChatListCreateView.as_view(), name="chat-list-create"),
    path("chats/<int:chat_pk>/messages/", 
         views.MessageListCreateView.as_view(), 
         name="message-list-create"),
    path("chats/<int:pk>/", views.ChatDetailView.as_view(), name="chat-detail"),
    
    # Message endpoints
    path("chats/<int:chat_pk>/messages/<int:pk>/", 
         views.MessageDetailView.as_view(), 
         name="message-detail"),
    
    # Assistant response endpoint
    path("assistant/respond/", 
         views.AssistantResponseView.as_view(), 
         name="assistant-respond"),
]