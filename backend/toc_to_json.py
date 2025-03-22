import asyncio
from pdf2image import convert_from_path
import aiohttp
import json

import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Replace with your actual Gemini API key
GEMINI_URL = os.getenv("GEMINI_URL")

async def convert_toc_to_json(text: str) -> dict:
    """
    Use the Gemini language model to generate a JSON representation of a book's table of contents.
    The JSON should be structured with chapters as keys and within each chapter, lessons as keys with a list 
    of two integers representing, for example, start and end pages.
    
    Example output:
    {
      "chapter 1": {
          "lesson 1": [5,6],
          "lesson 2": [7,10]
      }
    }
    
    DO NOT include any additional text besides the JSON.
    """    
    print("Converting the text to json...")
    prompt = (
        "Convert the following book table of contents text into a JSON object. "
        "The JSON should have chapters as keys (e.g., 'chapter 1') and for each chapter, a dictionary "
        "of lessons with their page ranges as a list of two integers. For example:\n"
        "RETURN IT AS A JSON OBJECT WITH NOTHING ELSE IN THE RESPONSE.\n\n"
        "Example JSON format:\n"
        '{\n'
        '  "chapter 1": {"lesson 1": [5,6], "lesson 2": [7,10]}\n'
        '}\n'
        "DO NOT include any additional text besides the JSON.\n\n"
        "Text:\n" + text
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_URL, headers=headers, json=payload) as response:
            if response.status == 503:
                print("Server is busy, retrying in 15 seconds...")
                await asyncio.sleep(15)
                return await convert_toc_to_json(text)
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Error: {response.status} - {error_text}")
            result = await response.json()
            
            candidate = result["candidates"][0]
            json_text = candidate.get("output") or candidate.get("content")
            if not json_text:
                raise Exception("JSON text not found in candidate response: " + str(candidate))
            
            # try:
                # toc_json = json.loads(json_text)
            # except json.JSONDecodeError as e:
                # raise Exception("Failed to decode JSON: " + str(e))
            
            return json_text["parts"][0]["text"]

async def remove_newline_tab(text: str) -> str:
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("```json", " ")
    text = text.replace("```", " ")
    return text

async def toc_to_json(text: str):
    extracted_text = text
    toc_json = await convert_toc_to_json(extracted_text)
    clean_toc = await remove_newline_tab(toc_json)

    while True:
        try:
            json_toc = json.loads(clean_toc)
            print("JSON successfully decoded.")
            break
        except json.JSONDecodeError as e:
            print("Failed to decode JSON, retrying...")
            toc_json = await convert_toc_to_json(extracted_text)
            clean_toc = await remove_newline_tab(toc_json)

    return json_toc
   
