from django.urls import path
from gpt.views import ChatWithGPTAPIView


urlpatterns = [
    path("chat/", ChatWithGPTAPIView.as_view()),
]