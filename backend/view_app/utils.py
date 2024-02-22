"""
This file is for any helper functions that 
calculate or do a specific thing that dont necessirly 
handle any HTTP requests or anything related to views
"""
#imports
import openai
import os
from dotenv import load_dotenv, find_dotenv
from scipy import linalg
from llama_index.embeddings import HuggingFaceEmbedding
from youtube_search import YoutubeSearch
import azure.cognitiveservices.speech as speechsdk

def azure_connect():
    """
    Connects to Azure
    """
    _ = load_dotenv(find_dotenv())
    openai.api_type = "azure"
    openai.api_base = os.getenv("OPENAI_API_BASE")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")

    print(openai.api_key)

def get_chatbot_response(user_input): #user_input = query
    """
    Takes user_query and returns chatgpt response
    parameter:
        user_input: query user enters
    """
    delimiter = "~~~~"
    system_message = f"""
    You are a chatbot, answer the questions given to you.
    The query will be delimited with four tildes, i.e. {delimiter}. 
    """
    # Prepare user input in the format required by OpenAI's chat models
    messages = [
        {'role':'system', 'content':system_message},
        {'role':'user', 'content':f'{delimiter}{user_input}{delimiter}'}
    ]
    try:
        # Make an OpenAI API call for chat completion
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=messages,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        
        # Extract the generated content from the API response
        response = response.choices[0].message.content
        return response

    except Exception as e:
        # Return an error message if an exception occurs during the API call
        return str(e)

# def speech_sdk_connect():
#     """
#     Connect to speech SDK
#     """
#     SPEECH_SERVICE_KEY="b0f5184c6c2242f78356246fb06082f9"
#     SPEECH_SERVICE_LOCATION="eastus"
#     SPEECH_SERVICE_ENDPOINT="https://eastus.api.cognitive.microsoft.com/"
#     return SPEECH_SERVICE_KEY, SPEECH_SERVICE_LOCATION

# def speech_to_text(language):
#     """
#     Speech to text function, will generate the query that will be sent to chatgpt
#     parameters: 
#         language: language being spoken (ar-EG / en-US / fr-FR / ja-JP)
#     """
#     #connect to speech sdk
#     SPEECH_SERVICE_KEY, SPEECH_SERVICE_LOCATION = speech_sdk_connect()

#     speech_to_text_config  = speechsdk.SpeechConfig(
#         subscription=SPEECH_SERVICE_KEY, region=SPEECH_SERVICE_LOCATION
#     )
#     speech_to_text_config.speech_recognition_language = language
#     audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
#     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_to_text_config, audio_config=audio_config)
#     print("Speak into your microphone.")
#     speech_recognition_result = speech_recognizer.recognize_once_async().get()
#     if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         print(f"Recognized: {speech_recognition_result.text}")
#         return speech_recognition_result.text
#     elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
#         print(f"No speech could be recognized: {speech_recognition_result.no_match_details}")
#     elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = speech_recognition_result.cancellation_details
#         print(f"Speech Recognition canceled: {cancellation_details.reason}")
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print(f"Error details: {cancellation_details.error_details}")
#             print("Did you set the speech resource key and region values?")

# def text_to_speech(voice_name, response):
#     """
#     The generated response that gpt sends back after query will be spoken using this function
#     parameters:
#         voice_name: name of voice (ar-EG-SalmaNeural / en-AU-NatashaNeural / fr-FR-DeniseNeural / ja-JP-NanamiNeural)
#         response: the response text sent from chatgpt that will be voice generated
#     """
#     #connect to speech sdk
#     SPEECH_SERVICE_KEY, SPEECH_SERVICE_LOCATION = speech_sdk_connect()

#     text_to_speech_config = speechsdk.SpeechConfig(
#         subscription=SPEECH_SERVICE_KEY, region=SPEECH_SERVICE_LOCATION
#     )
#     audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

#     # The language of the voice that speaks.
#     text_to_speech_config.speech_synthesis_voice_name = voice_name

#     speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=text_to_speech_config, audio_config=audio_config)

#     speech_synthesis_result = speech_synthesizer.speak_text_async(response).get()

#     if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#         print(f"Speech synthesized for text [{response}]")
#     elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = speech_synthesis_result.cancellation_details
#         print(f"Speech synthesis canceled: {cancellation_details.reason}")
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             if cancellation_details.error_details:
#                 print(f"Error details: {cancellation_details.error_details}")
#                 print("Did you set the speech resource key and region values?")

# def response_speech_and_text():
#     query = speech_to_text("en-US")
#     response = get_chatbot_response(query)
#     text_to_speech("en-AU-NatashaNeural", response)
#     return response

# def embed_column(column):
#     """
#     The given column gets embedded using HuggingFaceEmbedding model "BAAI/bge-small-en-v1.5"
#     parameter:
#         column: column to be embedded
#     """
#     embedding_model_HF = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5") # free open-source
#     text_embedding = embedding_model_HF.get_text_embedding(column)
#     return text_embedding

# def cos_sim(u, v):
#     """
#     This calculates cosine similarity between 2 vectors
#     parameters: 
#         u: first vector
#         v: second vector
#     """
#     numerator = u @ v
#     denominator = linalg.norm(u) * linalg.norm(v)
#     return numerator / denominator

# def search_youtube(query, max_results=10):
#     """
#     Get YouTube video IDs when searching for a query in an array
#     parameters:
#         query: query itself
#         max_results: number of IDs being sent back
#     """
#     # Get many information about YouTube video being queried
#     results = YoutubeSearch(query, max_results=max_results).to_dict()

#     # Get ids & url_suffix information from the results variable
#     videos_suffix = []
#     videos_ids = []
#     for video in results:
#         videos_suffix.append(video["url_suffix"][9:])
#         videos_ids.append(video["id"])
#     return videos_suffix, videos_ids