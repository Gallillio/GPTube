from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from .serializer import *
# from rest_framework.response import Response
from .utils import azure_connect, get_chatbot_response
from django.http import JsonResponse

def get_chatbot_response_ajax(request):
    # Connect to Azure OpenAI 
    azure_connect()

    if request.method == 'GET':
        query = request.GET.get('query')

        gpt_response = get_chatbot_response(query)

        return JsonResponse({"gpt_response": gpt_response})
    else:
        return JsonResponse({'gpt_response': "Method not allowed"}, status=405)