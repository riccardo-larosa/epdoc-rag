from query_data import query_rag
import streamlit as st


#create a streamlit app that interacts with LLM 
st.title("Chat with LLM")
st.write("This is a simple chatbot that uses the LLM model to generate responses.")
query_text = st.text_input("Enter your query here:","")

if st.button("Get Response"):
    response_text = query_rag(query_text)
    st.write(response_text)
