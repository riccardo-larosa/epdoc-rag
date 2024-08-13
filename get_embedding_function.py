from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
#from langchain_community.embeddings.bedrock import BedrockEmbeddings


def get_embedding_function():
   # embeddings = BedrockEmbeddings(credentials_profile_name="default", region_name="us-east-1")
    embeddings = OpenAIEmbeddings(),
   # embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings