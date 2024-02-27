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
        video_id, stopped_time = GetTimeAndID(request)
        gpt_response, use_scenario = GetChatboxResponse(query, video_id, stopped_time)

        # return JsonResponse({"gpt_response": gpt_response['output'], "use_scenario": use_scenario})
        return JsonResponse({"gpt_response": gpt_response, "use_scenario": use_scenario})
    else:
        return JsonResponse({'gpt_response': "Method not allowed"}, status=405)
    
def GetTimeAndID(request):
    if request.method == 'GET':
        stopped_time = request.GET.get('stoppedTime')
        video_id = request.GET.get('videoId')

        # Here you can process the stopped_time and video_id as needed
        # For now, let's just print them
        print("Stopped Time:", stopped_time)
        print("Video ID:", video_id)

        # You can return a JSON response confirming the receipt of data
        return stopped_time, video_id