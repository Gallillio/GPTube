"""
All side urls are kept here
"""
from django.urls import path
from .views import base, UseScenarioOrChatbotResponse, GetChatbotResponseAjax, GetTimeAndID, GetQuizAnswers, GetGenerateQuizJson
from django.urls import URLPattern

urlpatterns = [
    path('', base, name='base'),
    path('UseScenarioOrChatbotResponse/', UseScenarioOrChatbotResponse, name='UseScenarioOrChatbotResponse'),
    path('GetChatbotResponseAjax/', GetChatbotResponseAjax, name='GetChatbotResponseAjax'),
    path('GetTimeAndID/', GetTimeAndID, name='GetTimeAndID'),
    path('GetQuizAnswers/', GetQuizAnswers, name='GetQuizAnswers'),
    path('GetGenerateQuizJson/', GetGenerateQuizJson, name='GetGenerateQuizJson'),


]