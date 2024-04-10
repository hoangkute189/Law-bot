from django.urls import path
from .views import ChatEngineView, get_template


urlpatterns = [
    path('chat/', ChatEngineView.as_view(), name="chat-engine"),
    path('chat_template', get_template, name="font-end-template")
]