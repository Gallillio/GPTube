"""
All side urls are kept here
"""
from django.urls import path
from .views import base, GetChatbotResponseAjax
from django.urls import URLPattern

urlpatterns = [
    path('', base, name='base'),
    path('GetChatbotResponseAjax/', GetChatbotResponseAjax, name='GetChatbotResponseAjax'),
]