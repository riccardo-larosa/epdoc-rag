import streamlit as st
import os
from dotenv import load_dotenv
import ollama

from langchain.agents import initialize_agent, AgentType
#from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
#from langchain.chat_models import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from openai import OpenAI

from get_embedding_function import get_embedding_function

def get_vector_dbs():

    #read a comma separated list from the environment variable
    return os.getenv("VECTOR_DBS").split(",")

def extract_model_names(models_info: list) -> tuple:
    """
    Extracts the model names from the models information.

    :param models_info: A dictionary containing the models' information.

    Return:
        A tuple containing the model names.
    """
    models = list(model["name"] for model in models_info["models"])
    models.append("OPENAI")
    return tuple(models)

def main():
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    models_info = ollama.list()
    available_models = extract_model_names(models_info)
    if available_models:
        selected_model = st.selectbox("Pick a model ↓", available_models)

    available_vector_dbs = get_vector_dbs()
    if available_vector_dbs:
        vector_db = st.selectbox("Select a Vector Database", available_vector_dbs)
    else:
        st.warning("No Vector Databases available. Please set the VECTOR_DBS environment variable.")

    PROMPT_TEMPLATE = """
    Answer the question based only on the following context:
    {context}
    ---
    Answer the question based on the above context: {question}
    """

    st.title("🔎 Chat with EP Docs")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the EP Docs. How can I help you?"}
    ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input(placeholder="How do I create a promotion for 20% off for a new product?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

    # Prepare the DB.
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=vector_db, embedding_function=get_embedding_function())

    # Search the DB.
        results = db.similarity_search_with_score(prompt, k=5)
        print(results)

        context_text = "\n\n--------------------------\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=prompt)
        print(prompt)
        if selected_model=="OPENAI":
            print(f"Selected model: OPENAI with {OPENAI_API_KEY}")
            model = ChatOpenAI(temperature=0.7, api_key=OPENAI_API_KEY)
            response_text = model.invoke(prompt)
            print(response_text)
            response_text = response_text.content
        else:      
            print(f"Selected model: {selected_model}")
            model = Ollama(model=selected_model)
            response_text = model.invoke(prompt)


        sources =  [(doc.metadata.get("source", None), _score) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        #st.write(formatted_response)
        st.write(response_text)
        st.write(sources)
        


    #with st.chat_message("assistant"):
    #    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
    #    response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
    #    st.session_state.messages.append({"role": "assistant", "content": response})
    #    st.write(response)

if __name__ == "__main__":
    main()