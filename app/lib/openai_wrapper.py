import os, json
from dotenv import load_dotenv
import openai
from typing import List, Dict, Any

load_dotenv()

openAI_api_key = os.getenv("OPENAI_API_KEY", None)
azure_endpoint = os.getenv('OPENAI_API_ENDPOINT', None)
deployment_name = os.getenv('OPENAI_DEPLOYMENT_NAME', None)

if not openAI_api_key or not azure_endpoint or not deployment_name:
    raise ValueError("Please set the OPENAI_API_KEY, OPENAI_API_ENDPOINT, and OPENAI_DEPLOYMENT_NAME environment variables")

class OpenAI:
    def __init__(self, api_key: str=openAI_api_key, endpoint: str=azure_endpoint, deployment_name: str=deployment_name, api_version: str = "2023-03-15-preview", max_tokens: int = 1000, temperature: float = 0.7):
        """
        Initializes the Azure OpenAI wrapper.

        :param api_key: Azure OpenAI API Key
        :param endpoint: Azure OpenAI endpoint URL
        :param deployment_name: The model deployment name in Azure OpenAI
        :param api_version: API version (default: "2023-03-15-preview")
        """
        self.client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.deployment_name = deployment_name
    
    def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generates a chat response using Azure OpenAI.

        :param messages: List of messages in the format [{'role': 'user', 'content': 'Hello'}]
        :param max_tokens: Maximum tokens to generate
        :param temperature: Controls randomness (0: deterministic, 1: creative)
        :return: API response as a dictionary
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.model_dump()
        except Exception as e:
            return {"error": str(e)}
    
    def generate_embedding(self, input_text: str) -> Dict[str, Any]:
        """
        Generates an embedding for the given text.

        :param input_text: The input text to embed
        :return: API response as a dictionary
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=input_text
            )
            return response.model_dump()
        except Exception as e:
            return {"error": str(e)}