"""
All side urls are kept here
"""
from django.urls import path
from .views import base, UseScenarioOrChatbotResponse, GetChatbotResponseAjax, GetTimeAndID
from django.urls import URLPattern

urlpatterns = [
    path('', base, name='base'),
    path('UseScenarioOrChatbotRespons/e', UseScenarioOrChatbotResponse, name='UseScenarioOrChatbotResponse'),
    path('GetChatbotResponseAjax/', GetChatbotResponseAjax, name='GetChatbotResponseAjax'),
    path('GetTimeAndID/', GetTimeAndID, name='GetTimeAndID'),
]