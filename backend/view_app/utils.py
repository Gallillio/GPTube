"""
This file is for any helper functions that 
calculate or do a specific thing that dont necessirly 
handle any HTTP requests or anything related to views
"""
#imports
import openai
import os
from dotenv import load_dotenv, find_dotenv
from datetime import date, datetime
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import initialize_agent, load_tools, AgentType, Tool, AgentExecutor, Tool, ZeroShotAgent, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.tools import BaseTool

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
agent = None

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

def CompareDatesFunc(given_date):
    if "," in given_date:
        given_date = given_date.replace(",", "/")
    elif " " in given_date:
        given_date = given_date.replace(" ", "/")
    elif "-" in given_date:
        given_date = given_date.replace("-", "/")
    elif "." in given_date:
        given_date = given_date.replace(".", "/")
    given_date = datetime.strptime(given_date, "%d/%m/%Y").date()
    today_date = date.today()
    
    date_difference = (given_date - today_date).days
    return str(date_difference)

class CompareDatesTool(BaseTool):
    name = "Compare Dates"
    description = "use this tool when you have a date and need to subtract it from today's date"
    def _run(self, given_date: str = None,):
        # check for the values we have been given
        if given_date:
            return CompareDatesFunc(given_date)
        else:
            return "BAD BOI."
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

def MakeAgentWithMemory(model, tools):
    chat_history = MessagesPlaceholder(variable_name="chat_history")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        agent = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        tools = tools,
        llm = model,
        handle_parsing_errors = True,
        verbose = True,
        agent_kwargs={
            "memory_prompts": [chat_history],
            "input_variables": ["input", "agent_scratchpad", "chat_history"]
        },
        memory=memory,
    )
    return agent

def UseAgent():
    """
    This function is to properly add memory
    by using MakeAgentWithMemory()
    """
    model = ConnectToAzure()
    #All tools
    tools = [CompareDatesTool()]
    agent = MakeAgentWithMemory(model, tools)
    
    return agent

def GetChatboxResponse(user_input): #user_input = query
    """
    Takes user_query and returns chatgpt response
    parameter:
        user_input: query user enters
    """
    global agent
    if agent is None:
        # If agent is not initialized, call UseAgent() to initialize it
        agent = UseAgent()
    return agent(user_input)