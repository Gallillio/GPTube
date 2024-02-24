from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import ConnectToAzure, GetChatboxResponse
from django.http import JsonResponse

def base(request):
    return HttpResponse("<h2> go to /GetChatbotResponseAjax/")



def GetChatbotResponseAjax(request):
    # Connect to Azure OpenAI 
    # azure_connect()
    ConnectToAzure()

    if request.method == 'GET':
        query = request.GET.get('query')

        gpt_response = GetChatboxResponse(query)

        return JsonResponse({"gpt_response": gpt_response['output']})
    else:
        return JsonResponse({'gpt_response': "Method not allowed"}, status=405)