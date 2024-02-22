"""
All side urls are kept here
"""
from django.urls import path
from .views import get_chatbot_response_ajax

urlpatterns = [
    # path('', base, name='base'),
    path('get_chatbot_response_ajax/', get_chatbot_response_ajax, name='get_chatbot_response_ajax'),
]