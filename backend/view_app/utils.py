"""
This file is for any helper functions that 
calculate or do a specific thing that dont necessirly 
handle any HTTP requests or anything related to views
"""
#imports
import openai
import pandas as pd
import os
import faiss
from dotenv import load_dotenv, find_dotenv
from datetime import date, datetime
from langchain.chat_models import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, load_tools, AgentType, Tool, AgentExecutor, Tool, ZeroShotAgent, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory
from langchain.chains import ConversationChain
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

## Scenarios Section ##

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

def ConversationChainWithMemory(video_data, stopped_time):
    _DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.
    You're an AI Video Chat that helps people with anything he doesn't understand in the video given a transcript and stopped time
    Respond to the human as a professional bot and don't mention transcript word or something like this, we're here in a backend
    As an example:    Human: can you illustrate the last five mins
    AI: --respond here from the transcript and given time 
    
    Relevant pieces of previous conversation:
    {history}

    (You do not need to use these pieces of information if not relevant)

    Video Stopped time: {stopped_time}
    Given Data: {given_data}

    (This is a given transcript of a video, it is given as a json format including a (startime of a specific text - duration of this specific text - the text itself) )
    Current conversation:
    Human: {input}
    AI:"""
    PROMPT = PromptTemplate(
        input_variables=["history", "input"], 
        template=_DEFAULT_TEMPLATE,
        partial_variables = {'given_data': video_data, 'stopped_time': stopped_time}
    )
    conversation = ConversationChain(
    llm = ConnectToAzure(),
    prompt =  PROMPT,
    memory = MemoryWithVectorStore(),
    verbose = False
)
    return conversation

def UseScenarioOrChatbot():
    # query = test me on this subject
    ...

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


def get_video_data(csv_file, video_id):
    """
    Function to read a CSV file and retrieve text data along with start and duration for a given video_id.

    Parameters:
    csv_file (str): Path to the CSV file.
    video_id (str): ID of the video to retrieve data for.

    Returns:
    str: JSON formatted string containing text data, start, and duration for the given video_id.
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Filter the DataFrame to get data for the given video_id
        video_data = df[df['video_id'] == video_id]

        # Extract text, start, and duration data
        video_text_data = [{"text": row['text'], "start": row['start'], "duration": row['duration']} for index, row in video_data.iterrows()]

        # Convert the extracted data to JSON format
        json_data = json.dumps(video_text_data, indent=4)

        return json_data

    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    

def GetChatboxResponse(user_input, video_id, stopped_time): #user_input = query
    """
    Takes user_query and returns chatgpt response
    use_scenario = False because text here will be displayed in chatbot
    parameter:
        user_input: query user enters
    """
    use_scenario = False
    global conversation

    if conversation is None:
    # If agent is not initialized, call UseAgent() to initialize it
    #     agent = UseAgent()
        csv_file = "data/videos_transcript.csv"
        video_data_json = get_video_data(csv_file, video_id)
        conversation = ConversationChainWithMemory(video_data_json, stopped_time)

    # print("\n\n\n\n", agent(user_input))
    # return agent(user_input), use_scenario

    # print("\n\n\n\n", chat.predict(input = user_input))
    return conversation.predict(input = user_input), use_scenario   

#response, user = GetChatboxResponse(user_input = 'Illustrate the last 60 seconds', video_id = '-9TdpdjDtAM', stopped_time = '90')
#print(f'Response = {response}')