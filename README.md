## 💻 Local Lllama-3 with RAG
This app runs locally using llama3. 
A RAG (Retrieval Augmented Generation) app in Python that can let you query/chat with data from EP Doc site. 
Uses Chroma as vector storage and langchain as a framework to make things simpler to work with 

Bonus: add a streamlit app


### How to get Started?

* Install ollama


* Install the required dependencies:
```bash
python3 -m venv myenv
source myenv/bin/activate
python3 -m pip install -r requirements.txt   


deactivate
```

* Load VectorDB using the PDFs in the data directory
```bash
python3 populate_database.py --pdf
```
Use the flag ```--reset``` to clear the database

* Query the data
```bash
python3 query_data.py "how many destination tickets can a player have?" 
```

* Load VectorDB using the recursive URL loader 
```bash
python3 populate_database.py --url https://elasticpath.dev/docs/commerce-manager/product-experience-manager/Products/overview   
```
Use the flag ```--reset``` to clear the database

* Query the data
```bash
python3 query_data.py "How do I manage an active subscription?" 
python3 query_data.py "I would like to create a product for jeans with legth and waist size. Give me all the steps to do that and some sample data"  
```

* Run the Streamlit App
```bash
streamlit run chat_with_llm.py 
```


- 

## Credit
A lot of this code comes from https://www.youtube.com/watch?v=2TJxpyO3ei4 

