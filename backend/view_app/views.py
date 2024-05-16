from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .utils import ConnectToAzure, GetChatboxResponse, GenerateQuizJson, RoutingResponse,QuizAsContext
from django.http import JsonResponse
from django.core.cache import cache
import json

def base(request):
    return HttpResponse("<h2> go to /GetChatbotResponseAjax/")

def GetChatbotResponseAjax(request):
    # Connect to Azure OpenAI 
    ConnectToAzure()
    
    if request.method == 'GET':
        query = request.GET.get('query')
        videoId = request.GET.get('videoId')
        stopped_time = None
        response = RoutingResponse(query)
        # print(response, "\n ======================================")
        # quiz scenario
        if "quiz" in response.lower():
            print("\n\n", "Quiz Scenario", "\n\n")
            GetGenerateQuizJson(request, query)

            gpt_response = "Quiz has been generated in the Scenario Section"
            use_scenario = True
        elif "pp" in response.lower():
            print("\n\n", "Presentation Scenario", "\n\n")
            # GetGenerateQuizJson(request, query)

            gpt_response = "Presentation has been generated in the Scenario Section"
            use_scenario = True
        # normal message
        else:
            print("\n\n", "chat message scenario", "\n\n")
            # Attempt to read stopped_time and video_id from file
            try:
                with open("video_data/video_data.json", "r") as f:
                    data = json.load(f)
                stopped_time = data.get('Stopped_Time', stopped_time)
            except FileNotFoundError:
                pass  # File doesn't exist yet
            except Exception as e:
                return JsonResponse({"gpt_response": "Error occurred: " + str(e)}, status=500)

            # print("Stopped Time wohooo:", stopped_time)
        
            gpt_response, use_scenario = GetChatboxResponse(query, videoId, stopped_time)
            # print("\n\n\n\n\n gpt_response: \n", gpt_response, "\n\n\n\n\n")

        if gpt_response:
            return JsonResponse({"gpt_response": gpt_response, "use_scenario": use_scenario, "videoId": videoId})
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
        with open("video_data.json", "w") as f:
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
def GetGenerateQuizJson(request, input):
    csv_file = "video_data/reformatted_transcript.csv"
    if request.method == 'GET':
        video_id = request.GET.get('videoId')
        Quiz = GenerateQuizJson(video_id, csv_file, input)
        # print("Quiz: \n", Quiz)
        return JsonResponse({"quiz": Quiz})
    
def GetQuizAnswers(request):
    if request.method == 'GET':
    # To get the correct answers
        with open('quiz_scenario_JSON.json', 'r') as file:
            data = json.load(file)
        
        # To get the user answers
        quiz_scenario_user_answers_string = request.GET.get('quiz_scenario_user_answers')
        quiz_scenario_user_answers_JSON = json.loads(quiz_scenario_user_answers_string)
        
        # Extract choices and questions
        choices = [item.get('options') for item in data]
        questions = [item.get('question') for item in data]
        stopped_time = request.GET.get('stoppedTime')

        # Printing for debugging
        # print("\nUser Answers JSON: ", quiz_scenario_user_answers_JSON)
        # print("keys",quiz_scenario_user_answers_JSON.key())
        # print("vals")

        # Compare user answers with correct answers and save details of wrong answers
        wrong_answers = []
        for user_ans, correct_ans, question, choice in zip(quiz_scenario_user_answers_JSON.values(), 
                                                        [item.get('answer') for item in data], 
                                                        questions, 
                                                        choices):
            if user_ans != correct_ans:
                wrong_answers.append({
                    'question': question,
                    'user_answer': user_ans,
                    'correct_answer': correct_ans,
                    'choices': choice,
                })

        # Provide feedback or take further actions based on wrong_answers
        if not wrong_answers:
            response_message = "Congratulations! All answers are correct."
        else:
            response_message = f"You got {len(data) - len(wrong_answers)} out of {len(data)} answers correct. Here are the details of your wrong answers:"
            for wrong_answer in wrong_answers:
                response_message += f"\n\n Question: {wrong_answer['question']}\n Your Answer: {wrong_answer['user_answer']}\nCorrect Answer: {wrong_answer['correct_answer']}\nChoices: {wrong_answer['choices']}"
                
        
        gpt_response = QuizAsContext(response_message, stopped_time)

        return JsonResponse({"quiz_scenario_user_answers_response": gpt_response})
    
# time_and_id_response = GetTimeAndID(HttpResponse("<h2> go to /GetChatbotResponseAjax/"))
# stopped_time = time_and_id_response.get('Stopped_Time', stopped_time)
# video_id = time_and_id_response.get('Video_ID', video_id)
