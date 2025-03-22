"""
This file is for any helper functions that 
calculate or do a specific thing that dont necessirly 
handle any HTTP requests or anything related to views
"""
import google.generativeai as genai
import json
import pandas as pd
import os
import faiss
from dotenv import load_dotenv, find_dotenv
from sentence_transformers import SentenceTransformer
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.memory import VectorStoreRetrieverMemory, ConversationSummaryBufferMemory
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import aiohttp
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
conversation = None

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_URL")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

async def get_gemini_response(prompt: str) -> str:
    """
    Get a response from Gemini API with retry logic and proper error handling
    """
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            GEMINI_URL,
            headers=headers,
            json=payload,
            params={"key": GEMINI_API_KEY}
        ) as response:
            if response.status == 503:
                print("Server is busy, retrying in 15 seconds...")
                await asyncio.sleep(15)
                return await get_gemini_response(prompt)
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Error: {response.status} - {error_text}")
            result = await response.json()
            candidate = result["candidates"][0]
            return candidate.get("content", {}).get("parts", [{}])[0].get("text", "")

def run_async(coro):
    """Helper function to run async code in synchronous context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result

def ConnectToGemini():
    """
    desc:
        Function connects to Google Gemini API
    return: 
        model of llm
    """
    return model

def ConnectToE5Embedding():
    return SentenceTransformer("intfloat/multilingual-e5-base")

def RagWithFaiss(question, context):
    model = ConnectToE5Embedding()
    question_embedding = model.encode([question])
    paragraph_embedding = model.encode(context)
    d = question_embedding.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(paragraph_embedding)
    D, I = index.search(question_embedding, k = 3)  # search
    I = I[0]
    context = [context[k] for k in I]
    return context

def MemoryWithVectorStore():
    embeddings = ConnectToE5Embedding()
    embedding_size = 768  # Dimensions of the E5 embeddings
    index = faiss.IndexFlatL2(embedding_size)
    embedding_fn = embeddings.encode
    vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {})
    retriever = vectorstore.as_retriever(search_kwargs=dict(k=4))
    return VectorStoreRetrieverMemory(retriever=retriever)

def SummarizationMemory():
    # Create a LangChain-compatible LLM
    langchain_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)
    return ConversationSummaryBufferMemory(llm=langchain_model, max_token_limit=1000, memory_key="history", input_key='input')

def ConversationChainWithMemory(video_data, stopped_time):
    _DEFAULT_TEMPLATE = """
    You're an AI video chat that helps people with anything they don't understand in the video using the below transcript and stopped time.
    Respond to the human as a professional bot and don't mention 'transcript' word or something like this, we're here in a backend,
    but if the question or what he said is normal like hello or telling his name (talking like a friend) respond normally as an AI.
    Any questions that you can respond as an AI, Don't hesitate to respond.
    Respond to anything related to the video as illustration, summarization and generating questions from the video.
    
    Video Stopped time: ///{stopped_time}///
    This Video stopped time is used if the user asked to illustrate or summarize the last minute before the stopped time or summarize the after. 
    
    Video Transcript: ""{given_data}""

    (Video Transcript is a given transcript of a video, it is given as a text format including a 
    (the text in this minute - the minute from and to (example: (1-2))) 
    Use the minute to know from the stopped time of the video where is the specific time the user talking about and 
    responding with data relevant to that time (like if he asked to illustrate last 5 mins)).
    or asked: 'can you test my knowledge from what I heard so far', you should know where he stopped , what is the part
    is he asking about, so you should respond here with knowing the text that he stopped at and all the previous texts from the transcript
    the transcript and the stopped time are given above so don't ask the user about them.
    After all of these you should be able to respond to any question related to the video so don't tell the user 
    'Could you please let me know the specific part of the video you would like to be tested on?'.
    
    History of the conversation:
    {history}
    
    Current conversation:
    New human question: {input}
    Response:"""

    prompt = PromptTemplate(
        input_variables=["history", "input", "stopped_time", 'given_data'], template=_DEFAULT_TEMPLATE
    )

    # Create a LangChain-compatible LLM
    langchain_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)
    
    conversation = LLMChain(
        llm=langchain_model,
        prompt=prompt,
        verbose=True,
        memory=SummarizationMemory(),
    )
    return conversation

def get_video_data_txt(csv_file, video_id):
    """
    Function to read a CSV file and retrieve text data grouped by minute for a given video_id.

    Parameters:
    csv_file (str): Path to the CSV file.
    video_id (str): ID of the video to retrieve data for.

    Returns:
    dict: Dictionary containing the transcript data grouped by minute.
    """
    try:
    # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Filter the DataFrame to get data for the given video_id
        video_data = df[df['video_id'] == video_id]

        # Initialize a dictionary to hold the transcript data
        transcript_list = []

        # Iterate over the rows and group text by minute
        for index, row in video_data.iterrows():
            minute = row['minute']
            text = row['text']

            formatted_text = f"text: {text}, minute = {minute}"

            transcript_list.append(formatted_text)

        return transcript_list
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        return ""
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

def GenerateQuizJson(video_id, csv_file, input):
    question_schema = ResponseSchema(name="question",
                             description="The question")
    options_schema = ResponseSchema(name="options",
                                      description="A dictionary that contains A, B, C, D")
    answer_schema = ResponseSchema(name="answer",
                                    description="The answer of the question")

    response_schemas = [question_schema, 
                        options_schema,
                        answer_schema]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = '''
[
  {
    "question": "1. What is supervised machine learning?",
    "options": [
      {
        "A": "A. A type of learning where the model learns from labeled data.",
        "B": "B. A type of learning where the model learns from unlabeled data.",
        "C": "C. A type of learning where the model learns from reinforcement.",
        "D": "D. A type of learning where the model learns from semi-labeled data."
      }
    ],
    "answer": "A"
  },
  {
    "question": "2. Which of the following is an example of supervised learning algorithm?",
    "options": [
      {
        "A": "A. K-Means clustering",
        "B": "B. Decision tree",
        "C": "C. K-Nearest Neighbors",
        "D": "D. Apriori algorithm"
      }
    ],
    "answer": "B"
  }
]
  '''
    quiz_template = """\
    From the transcript, generate number of mcq questions (number specified by user) and if the user
     didn't specify a number, generate 5 questions by default :

    The output should be formatted as the following schema:

    {format_instructions}


    transcript: {text}

    User question: {input}
    """
    video_data = get_video_data_txt(csv_file, video_id)
    
    # Create the prompt as a single string instead of LangChain messages
    formatted_prompt = quiz_template.format(
        text=video_data, 
        format_instructions=format_instructions,
        input=input
    )
    
    # Use Google's Gemini API directly
    chat = ConnectToGemini()
    quiz = chat.generate_content(formatted_prompt)
    
    parser = JsonOutputParser()
    quiz_dict = parser.parse(quiz.text)
    file_name = "./../src/quiz_scenario_JSON.json"
    
    with open(file_name, 'w') as json_file:
        json.dump(quiz_dict, json_file)
    file_name_back = "./quiz_scenario_JSON.json"
    with open(file_name_back, 'w') as json_file:
        json.dump(quiz_dict, json_file)
    return quiz_dict

def GetChatboxResponse(user_input, video_id, stopped_time):
    """
    Takes user_query and returns Gemini response
    use_scenario = False because text here will be displayed in chatbot
    parameter:
        user_input: query user enters
    """
    if user_input and video_id and stopped_time:
        use_scenario = False
        global conversation
        csv_file = "video_data/reformatted_transcript.csv"
        video_data = get_video_data_txt(csv_file, video_id)
        context = RagWithFaiss(user_input, video_data)
        
        if conversation is None:
            conversation = ConversationChainWithMemory(video_data, stopped_time)
            return conversation.predict(input = user_input, stopped_time = stopped_time, given_data = context), use_scenario  
        else:
            return conversation.predict(input = user_input, stopped_time = stopped_time, given_data = context), use_scenario

def RoutingResponse(user_input):
    # Simple keyword-based classification to avoid model confusion
    user_input_lower = user_input.lower()
    
    # Check for quiz-related keywords
    if any(keyword in user_input_lower for keyword in ["quiz", "test me", "test my knowledge", "generate questions", "create a quiz"]):
        return "Quiz"
    
    # Check for powerpoint-related keywords
    if any(keyword in user_input_lower for keyword in ["powerpoint", "presentation", "slides", "ppt", "make a presentation"]):
        return "pp"
    
    # Default case for regular questions
    return "Default"

def QuizAsContext(input,stopped_time):
        video_data = input

        global conversation
        
        if conversation is None:
            conversation = ConversationChainWithMemory(video_data, stopped_time)
            return conversation.predict(input = input , stopped_time = stopped_time , given_data = video_data) 
        else:
            return conversation.predict(input = input ,stopped_time = stopped_time  , given_data = video_data)

def RefreshVideoList():
    df = pd.read_csv("video_data/reformatted_transcript.csv")
    video_dict = df[['video_id', 'video_name']].drop_duplicates().set_index('video_id').to_dict()['video_name']

    return video_dict

def GeneratePowerPointJson(video_id, csv_file, input):
    """
    Generate PowerPoint slides in JSON format based on video transcript
    """
    ppt_template = """\
    From the transcript, create an educational PowerPoint presentation. Generate between 5-8 slides including:
    - A title slide
    - Content slides with key points from the transcript
    - A summary slide
    
    The output should be formatted as the following JSON schema:
    [
      {{
        "title": "Introduction to Machine Learning",
        "content": [
          "Machine learning is a branch of artificial intelligence",
          "It enables computers to learn without explicit programming",
          "Growing field with many real-world applications"
        ],
        "note": "Optional presenter notes about this slide"
      }},
      {{
        "title": "Types of Machine Learning",
        "content": [
          "Supervised Learning: Training with labeled data",
          "Unsupervised Learning: Finding patterns in unlabeled data",
          "Reinforcement Learning: Learning through trial and error"
        ],
        "note": "Briefly explain each type with examples if time permits"
      }}
    ]
    
    Ensure the slides are educational, concise, and capture the main concepts from the transcript.
    Each slide should have a clear title and 2-5 bullet points as content.
    Create slides that flow logically from introduction to conclusion.

    transcript: {text}

    User request: {input}
    """
    
    video_data = get_video_data_txt(csv_file, video_id)
    
    # Create the prompt as a single string
    formatted_prompt = ppt_template.format(
        text=video_data,
        input=input
    )
    
    # Use Google's Gemini API directly
    chat = ConnectToGemini()
    presentation = chat.generate_content(formatted_prompt)
    
    try:
        # Parse the JSON response
        parser = JsonOutputParser()
        slides_dict = parser.parse(presentation.text)
        
        # Save to files
        file_name = "./../src/powerpoint_scenario_JSON.json"
        with open(file_name, 'w') as json_file:
            json.dump(slides_dict, json_file)
            
        file_name_back = "./powerpoint_scenario_JSON.json"
        with open(file_name_back, 'w') as json_file:
            json.dump(slides_dict, json_file)
            
        return slides_dict
    except Exception as e:
        print(f"Error parsing presentation: {e}")
        # If JSON parsing fails, attempt to extract JSON from the text response
        import re
        json_match = re.search(r'\[\s*\{.*\}\s*\]', presentation.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            slides_dict = json.loads(json_str)
            
            # Save to files
            file_name = "./../src/powerpoint_scenario_JSON.json"
            with open(file_name, 'w') as json_file:
                json.dump(slides_dict, json_file)
                
            file_name_back = "./powerpoint_scenario_JSON.json"
            with open(file_name_back, 'w') as json_file:
                json.dump(slides_dict, json_file)
                
            return slides_dict
        else:
            # If all parsing fails, return a default presentation
            default_slides = [
                {
                    "title": "Error Creating Presentation",
                    "content": [
                        "Could not generate presentation from transcript",
                        "Please try again with different phrasing"
                    ],
                    "note": "Error occurred during presentation generation"
                }
            ]
            
            # Save default slides
            file_name = "./../src/powerpoint_scenario_JSON.json"
            with open(file_name, 'w') as json_file:
                json.dump(default_slides, json_file)
                
            file_name_back = "./powerpoint_scenario_JSON.json"
            with open(file_name_back, 'w') as json_file:
                json.dump(default_slides, json_file)
                
            return default_slides