from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .utils import ConnectToAzure, GetChatboxResponse
from django.http import JsonResponse

def base(request):
    return HttpResponse("<h2> go to /GetChatbotResponseAjax/")

def UseScenarioOrChatbotResponse(request):
    # Connect to Azure OpenAI 
    ConnectToAzure()

    if request.method == 'GET':
        query = request.GET.get('query')

def GetChatbotResponseAjax(request):
    # Connect to Azure OpenAI 
    ConnectToAzure()

    if request.method == 'GET':
        query = request.GET.get('query')

        gpt_response, use_scenario = GetChatboxResponse(query)

        # return JsonResponse({"gpt_response": gpt_response['output'], "use_scenario": use_scenario})
        return JsonResponse({"gpt_response": gpt_response, "use_scenario": use_scenario})
    else:
        return JsonResponse({'gpt_response': "Method not allowed"}, status=405)