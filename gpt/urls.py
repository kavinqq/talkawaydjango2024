from django.urls import path
from gpt.views import ChatWithGPTAPIView, DellETestAPIView


urlpatterns = [
    path("chat/", ChatWithGPTAPIView.as_view()),
    path("image/", DellETestAPIView.as_view())
]