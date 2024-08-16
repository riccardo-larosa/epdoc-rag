from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
#from langchain_community.embeddings.bedrock import BedrockEmbeddings
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
import os

def get_embedding_function():
   load_dotenv()
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   # embeddings = BedrockEmbeddings(credentials_profile_name="default", region_name="us-east-1")
   #embeddings = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY,
   #                                                         model_name="text-embedding-3-small"),
   embeddings = OllamaEmbeddings(model="nomic-embed-text")
   return embeddings

