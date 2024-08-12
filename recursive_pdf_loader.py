from langchain_community.document_loaders import PyPDFDirectoryLoader


def get_pdfs(data_path):
    document_loader = PyPDFDirectoryLoader(data_path)
    return document_loader.load()
