from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .utils import ConnectToAzure, GetChatboxResponse
from django.http import JsonResponse
from django.core.cache import cache
import json

def base(request):
    return HttpResponse("<h2> go to /GetChatbotResponseAjax/")

def UseScenarioOrChatbotResponse(request):
    # Connect to Azure OpenAI 
    ConnectToAzure()

    if request.method == 'GET':
        query = request.GET.get('query')
        videoId = request.GET.get('videoId')

def GetChatbotResponseAjax(request):
    # Connect to Azure OpenAI 
    ConnectToAzure()
    
    if request.method == 'GET':
        query = request.GET.get('query')
        videoId = request.GET.get('videoId')
        stopped_time = None
        # Attempt to read stopped_time and video_id from file
        try:
            with open("video_data/video_data.json", "r") as f:
                data = json.load(f)
            stopped_time = data.get('Stopped_Time', stopped_time)
        except FileNotFoundError:
            pass  # File doesn't exist yet
        except Exception as e:
            return JsonResponse({'gpt_response': "Error occurred: " + str(e)}, status=500)

        print("Stopped Time wohooo:", stopped_time)
        
        gpt_response, use_scenario, Quiz = GetChatboxResponse(query, videoId, stopped_time)

        return JsonResponse({"gpt_response": gpt_response, "use_scenario": use_scenario, "videoId": videoId, "quiz": Quiz})
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

        # Save stopped_time and video_id to a file
        data = {"Stopped_Time": stopped_time}
        with open("video_data/video_data.json", "w") as f:
            json.dump(data, f)

        # You can return a JSON response confirming the receipt of data
        return JsonResponse(data)
    else:
        # Read from the file if it exists
        try:
            with open("video_data/video_data.json", "r") as f:
                data = json.load(f)
            return JsonResponse(data)
        except FileNotFoundError:
            return JsonResponse({'Stopped_Time': None, 'Video_ID': None})
        except Exception as e:
            return JsonResponse({'Stopped_Time': "Error occurred: " + str(e)}, status=500)


# time_and_id_response = GetTimeAndID(HttpResponse("<h2> go to /GetChatbotResponseAjax/"))
# stopped_time = time_and_id_response.get('Stopped_Time', stopped_time)
# video_id = time_and_id_response.get('Video_ID', video_id)
