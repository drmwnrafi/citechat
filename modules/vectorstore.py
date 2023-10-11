from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import modules.file_chunking as fc
import os

def load_embeddings(model_name:str):
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs = {'device': 'cpu'})
    return embeddings

def build_vectorstore(chunks, embeddings):
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vectorstore/faiss")
    return vectorstore

def get_files_vdb(vdb):
    v_dict=vdb.docstore._dict
    data_rows=[]
    for k in v_dict.keys():
        doc = v_dict[k].metadata['source'].split('/')[-1]
        data_rows.append(doc)
    return set(data_rows)

def add_docs(paths, embeddings):
    vdb_path =os.path.join(os.getcwd(), "vectorstore/faiss")
    
    if os.path.exists(vdb_path):
        vdb = FAISS.load_local(vdb_path, embeddings)

        if paths == ".": 
            return vdb
        
        elif len(paths)>1:
            file_on_vdb = get_files_vdb(vdb)
            paths = fc.extract_dir(paths)

            out_of_vdb = []
            for file_name in paths:
                if file_name not in file_on_vdb:
                    out_of_vdb.append(file_name)

            if out_of_vdb != []:
                docs = fc.load_file(out_of_vdb)
                chunks = fc.chunking_data(docs)
                vdb.add_documents(chunks) 
                vdb.save_local(vdb_path)
                msg = "PDFs Uploaded"

            elif out_of_vdb == []:    
                msg = "All PDFs already exist"
    else :
        if paths == ".": 
            msg = "Please Input Your Path"

        else :
            docs = fc.load_file(paths)
            chunks = fc.chunking_data(docs)
            vdb =  build_vectorstore(chunks, embeddings)
            msg = "Build vectorstore successfull"
            
    return vdb