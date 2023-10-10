from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
import os


def setup_dbqa(llm, vdb, memory):
    chain = ConversationalRetrievalChain.from_llm(llm, 
                                                  retriever=vdb.as_retriever(search_type="mmr", search_kwargs={'k': 2}), 
                                                  return_source_documents=True,
                                                  memory=memory,
                                                  chain_type="stuff",
                                                  verbose=True,
                                                  get_chat_history=lambda h :h,)
    return chain