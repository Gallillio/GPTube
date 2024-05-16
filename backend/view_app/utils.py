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

    (Video Transcript is a given transcript of a video, it is given as a dictionary format including a 
    (the minute from and to (example: (1-2))- the text in this minute) 
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

    conversation = LLMChain(
    llm=ConnectToAzure(),
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
        transcript_dict = {}

        # Iterate over the rows and group text by minute
        for index, row in video_data.iterrows():
            minute = row['minute']
            text = row['text']

            if minute in transcript_dict:
                transcript_dict[minute] += f" {text}"
            else:
                transcript_dict[minute] = text

        return transcript_dict
    
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
    prompt = ChatPromptTemplate.from_template(template=quiz_template)
    messages = prompt.format_messages(text=video_data, 
                                format_instructions=format_instructions,
                                input = input)
    chat = ConnectToAzure()
    quiz = chat(messages)
    parser = JsonOutputParser()
    quiz_dict = parser.parse(quiz.content)
    file_name = "./../src/quiz_scenario_JSON.json"
    
    with open(file_name, 'w') as json_file:
        json.dump(quiz_dict, json_file)
    file_name_back = "./quiz_scenario_JSON.json"
    with open(file_name_back, 'w') as json_file:
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
        csv_file = "video_data/reformatted_transcript.csv"
        video_data = get_video_data_txt(csv_file, video_id)
        
        if conversation is None:
            conversation = ConversationChainWithMemory(video_data, stopped_time)
            return conversation.predict(input = user_input, stopped_time = stopped_time, given_data = video_data), use_scenario  
        else:
            return conversation.predict(input = user_input, stopped_time = stopped_time, given_data = video_data), use_scenario

def RoutingResponse(user_input):
    chain = (
    ChatPromptTemplate.from_template(
        """Given the user prompt, it can be classified in 3 ways: `Default`, `Quiz` `pp`.
        I'll provide a description for each classification and you have to decide depending on the user prompt which class is most appropriate.
        Descriptions:
        - `Default`: used when user prompt is a question related to the video OR if the user question is a question ABOUT a quiz that they did, for example something along the lines of 'explain a question 2' or 'explain why answer B in question 3 is wrong'.
        - `Quiz`: used when the user prompt is for the AI to quiz him, this should ONLY be done when the user asks to be tested.
        - `pp`: used when the user prompt is for the AI to make a powerpoint presentation for him, ONLY use it in that case.

Do not respond with more than one word.

<question>
{question}
</question>

Classification:"""
    )
  )   
    chain = chain.invoke({"question": user_input}) 
    chat = ConnectToAzure()
    response = chat(chain.messages).content.lower()
    return response

def QuizAsContext(input,stopped_time):
        video_data = input

        global conversation
        
        if conversation is None:
            conversation = ConversationChainWithMemory(video_data, stopped_time)
            return conversation.predict(input = input , stopped_time = stopped_time , given_data = video_data) 
        else:
            return conversation.predict(input = input ,stopped_time = stopped_time  , given_data = video_data)
