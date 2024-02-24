from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import ConnectToAzure, get_chatbot_response
from django.http import JsonResponse

def base(request):
    return HttpResponse("<h2> go to /get_chatbot_response_ajax/")

def get_chatbot_response_ajax(request):
    # Connect to Azure OpenAI 
    # azure_connect()
    ConnectToAzure()

    if request.method == 'GET':
        query = request.GET.get('query')

        gpt_response = get_chatbot_response(query)

        return JsonResponse({"gpt_response": gpt_response['output']})
    else:
        return JsonResponse({'gpt_response': "Method not allowed"}, status=405)