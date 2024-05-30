"""
All side urls are kept here
"""
from django.urls import path
from .views import base, GetChatbotResponseAjax, GetTimeAndID, GetQuizAnswers, GetGenerateQuizJson, ChangeVideoID
from django.urls import URLPattern

urlpatterns = [
    path('', base, name='base'),
    path('GetChatbotResponseAjax/', GetChatbotResponseAjax, name='GetChatbotResponseAjax'),
    path('GetTimeAndID/', GetTimeAndID, name='GetTimeAndID'),
    path('GetQuizAnswers/', GetQuizAnswers, name='GetQuizAnswers'),
    path('GetGenerateQuizJson/', GetGenerateQuizJson, name='GetGenerateQuizJson'),
    path('ChangeVideoID/', ChangeVideoID, name='ChangeVideoID'),


]