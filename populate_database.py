import argparse
import os
import shutil
#from langchain.document_loaders.pdf import PyPDFDirectoryLoader
#from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from recursive_url_loader import get_urls_docs
from recursive_md_loader import get_md_files
from recursive_pdf_loader import get_pdfs
#from langchain.vectorstores.chroma import Chroma
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
import requests
from bs4 import BeautifulSoup
from langchain.schema.document import Document
#import urllib.parse

CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():

    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, help="The URL to process")
    parser.add_argument("--md", action="store_true", help="Process the MD files in the data directory.")
    parser.add_argument("--pdf", action="store_true", help="Process the PDFs in the data directory.")
    parser.add_argument("--data_path", type=str, help="The path to the data directory.")
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--vectordb_path", type=str, help="The path to the vector database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database(args.vectordb_path)

    if args.url: 
        # Load the documents from the webpage.
        url = args.url 
        print(f"🌐 Loading Documents from Webpage: {url}")
        documents = get_urls_docs(url)
    
    if args.pdf:
        # Create (or update) the data store using the PDFs in the data directory.
        DATA_PATH = args.data_path
        documents = get_pdfs(DATA_PATH)
    
    if args.md:
        DATA_PATH = args.data_path
        documents = get_md_files(DATA_PATH)

    #print(documents)
    if not documents:
        print("No documents to process.")
        return
    
    chunks = split_documents(documents)
    add_to_chroma(chunks, args.vectordb_path)



def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document], vectordb_path):
    # Load the existing database.
    if vectordb_path:
        CHROMA_PATH = vectordb_path
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )
    
    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
       #db.persist() #not needed anymore
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

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


def clear_database(vectordb_path):
    if os.path.exists(vectordb_path):
        shutil.rmtree(vectordb_path)


if __name__ == "__main__":
    main()