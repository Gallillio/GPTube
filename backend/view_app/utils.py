"""
This file is for any helper functions that 
calculate or do a specific thing that dont necessirly 
handle any HTTP requests or anything related to views
"""
#imports
#imports
import openai
import json
import pandas as pd
import os
import faiss
from dotenv import load_dotenv, find_dotenv
from datetime import date, datetime
from langchain.chat_models import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.agents import initialize_agent, load_tools, AgentType, Tool, AgentExecutor, Tool, ZeroShotAgent, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory, ConversationSummaryBufferMemory
from langchain.chains import ConversationChain, LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.tools import BaseTool

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
conversation = None

"""
if use scenario: use_scenario = True
if use chatbot: use_scenario = False
"""

def ConnectToAzure():
    """
    desc:
        Function connects to langchain AzureOpenAI
    return: 
        model of llm
    """
    ## Keys ##
    OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

    model = AzureChatOpenAI(
        openai_api_base=OPENAI_API_BASE,
        openai_api_version=OPENAI_API_VERSION,
        azure_deployment=DEPLOYMENT_NAME,
        openai_api_key=OPENAI_API_KEY,
        openai_api_type=OPENAI_API_TYPE,
    )
    return model

def ConnectToAzureEmbedding():
    OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_DEPLOYMENT_URL = os.getenv("OPENAI_API_DEPLOYMENT_URL")

    return AzureOpenAIEmbeddings(  
    openai_api_base=OPENAI_API_DEPLOYMENT_URL,
    openai_api_version=OPENAI_API_VERSION,
    openai_api_key=OPENAI_API_KEY,
    openai_api_type=OPENAI_API_TYPE,
)

def MemoryWithVectorStore():
    embeddings = ConnectToAzureEmbedding()
    embedding_size = 1536 # Dimensions of the OpenAIEmbeddings
    index = faiss.IndexFlatL2(embedding_size)
    embedding_fn = embeddings.embed_query
    vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {})
    retriever = vectorstore.as_retriever(search_kwargs=dict(k=4))
    return VectorStoreRetrieverMemory(retriever=retriever)

def GenerateQuizJson(video_id, csv_file):
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
    format_instructions = '''[
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
  },
  {
    "question": "3. What is the primary goal of supervised learning?",
    "options": [
      {
        "A": "A. To minimize error on the training data.",
        "B": "B. To maximize accuracy on the test data.",
        "C": "C. To generalize well on unseen data.",
        "D": "D. To memorize the training data."
      }
    ],
    "answer": "C"
  },
  {
    "question": "4. Which of the following tasks is NOT typically performed in supervised learning?",
    "options": [
      {
        "A": "A. Classification",
        "B": "B. Clustering",
        "C": "C. Regression",
        "D": "D. Anomaly detection"
      }
    ],
    "answer": "B"
  },
  {
    "question": "5. What is the process of supervised learning?",
    "options": [
      {
        "A": "A. Feature engineering, model selection, training, evaluation",
        "B": "B. Data collection, feature selection, training, deployment",
        "C": "C. Data preprocessing, model training, testing, deployment",
        "D": "D. Feature extraction, model validation, testing, deployment"
      }
    ],
    "answer": "C"
  }
]
  '''
    quiz_template = """\
    From the Transcript, generate 5 MCQ questions:

    The output should be formatted as the following schema:

    {format_instructions}


    text: {text}
    """
    video_data = get_video_data_txt(csv_file, video_id)
    prompt = ChatPromptTemplate.from_template(template=quiz_template)
    messages = prompt.format_messages(text=video_data, 
                                format_instructions=format_instructions)
    chat = ConnectToAzure()
    quiz = chat(messages)
    parser = JsonOutputParser()
    quiz_dict = parser.parse(quiz.content)
    file_name = "./../src/quiz_scenario_JSON.json"
    with open(file_name, 'w') as json_file:
        json.dump(quiz_dict, json_file)
    return quiz_dict

def SummarizationMemory():
    model = ConnectToAzure()
    return ConversationSummaryBufferMemory(llm=model, max_token_limit=1000, memory_key="history",  input_key='input')

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
    (the text itself - startime of a specific text - duration of this specific text) 
    Use the start time to know from the stopped time of the video where is the specific time the user talking about and 
    responding with data relevant to that time (like if he asked to illustrate last 5 mins)).
    to understand the concept, from the given stopped time search the stopped time in between the specific start times given in the transcript
    (as an example: if the the stopped time = 215.25 and there is two start times = 212.50 and 217.8 so choose the first start 212.50
    and choose the text in this start and respond using it and all its previous or after texts based on the user question) and respond,
    like if the user asked: 'can you test my knowledge from what I heard so far', you should know where he stopped what is the part
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

    conversation = LLMChain(
    llm=ConnectToAzure(),
    prompt=prompt,
    verbose=True,
    memory=SummarizationMemory(),
    )
    return conversation

def UseScenarioOrChatbot():
    # query = test me on this subject
    ...

def get_video_data_txt(csv_file, video_id):
    """
    Function to read a CSV file and retrieve text data along with start and duration for a given video_id.

    Parameters:
    csv_file (str): Path to the CSV file.
    video_id (str): ID of the video to retrieve data for.

    Returns:
    str: String containing the transcript data formatted as text, start, and duration.
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Filter the DataFrame to get data for the given video_id
        video_data = df[df['video_id'] == video_id]

        # Initialize a string to hold the transcript data
        transcript_data = f"Transcript of Video ID: {video_id}\n\n"

        # Iterate over the rows and append each entry as text, start, and duration
        for index, row in video_data.iterrows():
            transcript_data += f"Text: {row['text']}\n"
            transcript_data += f"Start: {row['start']}\n\n"

        return transcript_data
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        return ""
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

def GenerateQuizJson(video_id, csv_file):
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
    """
    video_data = get_video_data_txt(csv_file, video_id)
    prompt = ChatPromptTemplate.from_template(template=quiz_template)
    messages = prompt.format_messages(text=video_data, 
                                format_instructions=format_instructions)
    chat = ConnectToAzure()
    quiz = chat(messages)
    parser = JsonOutputParser()
    quiz_dict = parser.parse(quiz.content)
    file_name = "./../src/quiz_scenario_JSON.json"
    with open(file_name, 'w') as json_file:
        json.dump(quiz_dict, json_file)
    return quiz_dict

def GetChatboxResponse(user_input, video_id, stopped_time): #user_input = query
    """
    Takes user_query and returns chatgpt response
    use_scenario = False because text here will be displayed in chatbot
    parameter:
        user_input: query user enters
    """
    if user_input and video_id and stopped_time:

        use_scenario = False
        global conversation
        csv_file = "video_data/videos_transcript.csv"
        video_data = get_video_data_txt(csv_file, video_id)
        Quiz = GenerateQuizJson(video_id, csv_file)
        
        if conversation is None:
            conversation = ConversationChainWithMemory(video_data, stopped_time)
            return conversation.predict(input = user_input, stopped_time = stopped_time, given_data = video_data), use_scenario, Quiz   
        else:
            return conversation.predict(input = user_input, stopped_time = stopped_time, given_data = video_data), use_scenario, Quiz
    

            

#response, user = GetChatboxResponse(user_input = 'Illustrate the last 60 seconds', video_id = '-9TdpdjDtAM', stopped_time = '90')
#print(f'Response = {response}')
# csv_file = "data/videos_transcript.csv"

# video_data_json = get_video_data(csv_file, 'zgtepSTqzgc')
# print(video_data_json)


## CHATBOT SECTION ##

# def CompareDatesFunc(given_date):
#     if "," in given_date:
#         given_date = given_date.replace(",", "/")
#     elif " " in given_date:
#         given_date = given_date.replace(" ", "/")
#     elif "-" in given_date:
#         given_date = given_date.replace("-", "/")
#     elif "." in given_date:
#         given_date = given_date.replace(".", "/")
#     given_date = datetime.strptime(given_date, "%d/%m/%Y").date()
#     today_date = date.today()
    
#     date_difference = (given_date - today_date).days
#     return str(date_difference)

# class CompareDatesTool(BaseTool):
#     name = "Compare Dates"
#     description = "use this tool when you have a date and need to subtract it from today's date"
#     def _run(self, given_date: str = None,):
#         # check for the values we have been given
#         if given_date:
#             return CompareDatesFunc(given_date)
#         else:
#             return "BAD BOI."
        
#     def _arun(self, query: str):
#         raise NotImplementedError("This tool does not support async")

# def MakeAgentWithMemory(model, tools):
#     chat_history = MessagesPlaceholder(variable_name="chat_history")
#     #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
#     memory = MemoryWithVectorStore()
#     agent = initialize_agent(
#         agent = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#         tools = tools,
#         llm = model,
#         handle_parsing_errors = True,
#         verbose = True,
#         agent_kwargs={
#             "memory_prompts": [chat_history],
#             "input_variables": ["input", "agent_scratchpad", "chat_history"]
#         },
#         memory=memory,
#     )
#     return agent

# def UseAgent():
#     """
#     This function is to properly add memory
#     by using MakeAgentWithMemory()
#     """
#     model = ConnectToAzure()
#     #All tools
#     tools = [CompareDatesTool()]
#     agent = MakeAgentWithMemory(model, tools)
    
#     return agent