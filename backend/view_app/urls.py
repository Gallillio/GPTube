"""
All side urls are kept here
"""
from django.urls import path
from .views import base, get_chatbot_response_ajax
from django.urls import URLPattern

urlpatterns = [
    path('', base, name='base'),
    path('get_chatbot_response_ajax/', get_chatbot_response_ajax, name='get_chatbot_response_ajax'),
]