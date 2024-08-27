import yaml
import os
import tiktoken
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from openapi_spec_validator import validate_spec
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document


load_dotenv( override=True)
MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
DB_NAME = os.getenv("DB_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load the OpenAPI spec from a file
with open("./data_md/openapispecs/commerceextensions/OpenAPISpec.yaml", "r") as f:
    openapi_spec = yaml.safe_load(f)

    endpoints = [
        (route, operation)
        for route, operations in openapi_spec["paths"].items()
        for operation in operations
        if operation in ["get", "post"]
    ]
    print(f"Found {len(endpoints)} endpoints")

# Validate the spec (optional)
#validate_spec(openapi_spec)

# Initialize a dictionary to store structured data
api_data = {
    "tags": [],
    "paths": [],
    "schemas": {},
    "components": {}
}

if "tags" in openapi_spec:
    api_data["tags"] = openapi_spec["tags"]
    #print(f"\nTags: {api_data['tags']}")

chunks = []
# Extract paths and their operations
for path, path_item in openapi_spec.get('paths', {}).items():
    for method, operation in path_item.items():
        if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
            endpoint = {
                "method": method.upper(),
                "path": path,
                "summary": operation.get('summary', ''),
                "description": operation.get('description', ''),
                "operationId": operation.get('operationId', ''),
                "parameters": operation.get('parameters', []),
                "responses": operation.get('responses', {}),
                "requestBody": operation.get('requestBody', {})
            }
            api_data["paths"].append(endpoint)
            chunk = Document(page_content=str(endpoint), metadata=endpoint["metadata"])
            chunks.append(chunk)

# Extract components (e.g., schemas, parameters)
if "components" in openapi_spec:
    api_data["components"] = openapi_spec["components"]
    #print(f"\nComponents: {api_data['components']}")

# Extract schemas from components for later use
if "schemas" in api_data["components"]:
    api_data["schemas"] = api_data["components"]["schemas"]
    #print(f"\nSchemas: {api_data['schemas']}")

# Example: Print the structured data
#for endpoint in api_data["paths"]:
#    print(endpoint["path"], endpoint["method"],"\n", endpoint["summary"], "\n", endpoint["description"], "\n", endpoint["parameters"], "\n", endpoint["responses"], "\n", endpoint["requestBody"], "\n")
    
endpoint = api_data["paths"][5]
#print(endpoint["path"], endpoint["method"],"\n", 
#      f"summary: {endpoint["summary"]}\n",
#      f"desc: {endpoint["description"]}\n", 
#      f"params: {endpoint["parameters"]}\n", 
#      f"resp: {endpoint["responses"]}\n", 
#      f"reqbody: {endpoint["requestBody"]}\n")
    
#print(api_data["tags"])

# Save the structured data to db

client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
db_name = DB_NAME #"langchain_db"
collection_name = "openapi_spec" 
atlas_collection = client[db_name][collection_name]
vector_search_index = "vector_index"

# Create a MongoDBAtlasVectorSearch object
db = MongoDBAtlasVectorSearch.from_connection_string(
    MONGODB_ATLAS_CLUSTER_URI,
    db_name + "." + collection_name,
    OpenAIEmbeddings(disallowed_special=(), model="text-embedding-3-small") ,
    index_name = vector_search_index
)


def split_openapis(api_data):
    chunks = []
    for endpoint in api_data["paths"]:
        doc = {            
            "path": endpoint["path"],
            "method": endpoint["method"],
            "summary": endpoint["summary"] + " " + endpoint["description"],
            "metadata":{
                "path": endpoint["path"],
                "method": endpoint["method"],
                "parameters": endpoint["parameters"],
                "responses": endpoint["responses"],
                "requestBody": endpoint["requestBody"],
                "id": None,
                "source": endpoint["path"]
            }
        }
        chunk = Document(page_content=str(doc), metadata=doc["metadata"])
        chunks.append(chunk)
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo").encode(chunk.__str__())
        print(f"lenght of chunk {chunk.metadata.get("path")}:{chunk.metadata.get("method")} is {len(encoding)} tokens")
        #TODO: I really don't need all of this, I can just do this at the beginning 
        # in the big for loop and then just add the chunk to the db
        # also I need to save 

    return chunks


def calculate_chunk_ids(chunks):

    # This will create IDs like "/v2/settings/extensions/custom-apis:POST:2"
    # Path : Method : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        path = chunk.metadata.get("path")
        method = chunk.metadata.get("method")
        current_page_id = f"{path}:{method}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks

#chunks = split_openapis(api_data)
chunks_with_ids = calculate_chunk_ids(chunks)

print(f"👉 Adding new documents: {len(chunks)}")
new_chunk_ids = [chunk.metadata["id"] for chunk in chunks]
# delete all data from db
db.delete()
db.add_documents(documents=chunks, ids=new_chunk_ids)

#now let's search for something 

