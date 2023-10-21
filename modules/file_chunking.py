from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader
import os

def load_file(paths:list) :
    documents = []
    if os.path.isdir(str(paths)):
        loader = PyPDFDirectoryLoader(paths)
        documents = loader.load()
        return documents
    else:
        documents =[]
        for path in paths:
            loader = PyPDFLoader(path)
            documents.extend(loader.load_and_split())
        return documents

def chunking_data(docs:list):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    return chunks

def extract_dir(path):
    if os.path.isdir(path):
        files = os.listdir(path)
        path = [os.path.join(path, file) for file in files]
    return path
