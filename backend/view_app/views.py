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

def GetChatbotResponseAjax(request):
    # Connect to Azure OpenAI 
    ConnectToAzure()
    
    global stopped_time, video_id
    stopped_time = None  # Initialize stopped_time
    video_id = None  # Initialize video_id
    
    if request.method == 'GET':
        query = request.GET.get('query')
        
        # Attempt to read stopped_time and video_id from file
        try:
            with open("video_data/video_data.json", "r") as f:
                data = json.load(f)
            stopped_time = data.get('Stopped_Time', stopped_time)
            video_id = data.get('Video_ID', video_id)
        except FileNotFoundError:
            pass  # File doesn't exist yet
        except Exception as e:
            return JsonResponse({"gpt_response": "Error occurred: " + str(e)}, status=500)

        print("Stopped Time wohooo:", stopped_time)
        print("Video ID wohooo:", video_id)
        
        gpt_response, use_scenario = GetChatboxResponse(query, video_id, stopped_time)

        return JsonResponse({"gpt_response": gpt_response, "use_scenario": use_scenario})
    else:
        return JsonResponse({"gpt_response": "Method not allowed"}, status=405)

def GetTimeAndID(request):
    if request.method == 'GET':
        stopped_time = request.GET.get('stoppedTime')
        video_id = request.GET.get('videoId')

        # Here you can process the stopped_time and video_id as needed
        # For now, let's just print them
        print("Stopped Time:", stopped_time)
        print("Video ID:", video_id)

        # Save stopped_time and video_id to a file
        data = {"Stopped_Time": stopped_time, "Video_ID": video_id}
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

### SCENARIOS ###
def GetQuizScenarioJSON(request):
    if request.method == 'GET':
        quiz_scenario_user_answers_string = request.GET.get('quiz_scenario_user_answers')
        quiz_scenario_user_answers_JSON = json.loads(quiz_scenario_user_answers_string)
        print("\n\n\n ",quiz_scenario_user_answers_JSON, "\n\n\n")

        keys = quiz_scenario_user_answers_JSON.keys()
        values = quiz_scenario_user_answers_JSON.values()
        # print("KEYS: \n", keys, "\n\n")
        # print("VALUEES: \n", values, "\n\n")

        for key in keys:
            print("VALUES USING KEY: \n", quiz_scenario_user_answers_JSON[key] ,"\n")

        return JsonResponse({"quiz_scenario_user_answers_response": "great work, it worked, go check views.py to actually make it work you dumb fuk"})

# time_and_id_response = GetTimeAndID(HttpResponse("<h2> go to /GetChatbotResponseAjax/"))
# stopped_time = time_and_id_response.get('Stopped_Time', stopped_time)
# video_id = time_and_id_response.get('Video_ID', video_id)
