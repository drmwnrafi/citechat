from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from modules import llms as llms
from modules import keyword_extraction as key
import re


def setup_dbqa(llm, vdb, memory):
    chain = ConversationalRetrievalChain.from_llm(llm, 
                                                  retriever=vdb.as_retriever(search_type="mmr", search_kwargs={'k': 2}), 
                                                  return_source_documents=True,
                                                  memory=memory,
                                                  chain_type="stuff",
                                                  verbose=True,
                                                  get_chat_history=lambda h :h,)
    return chain

def llm_query(prompt):
    prompt_template = PromptTemplate.from_template(
        """
        Provide me with a powerful query for searching papers, integrating it with your existing knowledge related to the prompt.
        The prompt is **{prompt}**. 
        Combine prompt with your existing knowledge that related to the prompt.
        
        Give me the query with this format, don't using boolean operators, and without using a question sentence or a question mark:
        <start_format>**[Query : <fill query here>]**<end_format>

        Do not put link on your response. <star_format> and <end_format> are a padding, so don't included them for the response output
        Just give me a query without any explaination. You must to follow my query format above don't forget the "[]".
        The <start_format> and <end_format> are for padding and should not be included in your response. Keep the query concise and within a reasonable length.
        Please respond with just the query; no explanations before or after the query. Your response should be one line..
        """
    )
    return prompt_template.format(prompt=prompt)

def get_query_search(prompt):
    llm = llms.BardLLM()
    response = llm(llm_query(prompt))
    patterns = [
        r'\*\*\[Query\s*:\s*(.*?)\]\*\*',
        r'<start_format>\*\*Query\s*:\s*(.*?)\*\*<end_format>',
        r'\*\*Query:\*\*\s*\[(.*?)\]',
        r"\*\*Query:\*\*\s+(.*?)\*\*",
        r"\[Query:\s(.*?)\]",
        r"\*\*Query:\*\*\s(.*?)$", 
        r"Query:\s+\*\*(.*?)\*\*",
        r"\*\*\[Query:\s(.*?)\]\*\*",
        r"\*\*Query:\*\*[\n\s]*\n([\s\S]*)",
    ]
    query = None
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            query = match.group(1)
            break
    if query == None or response == None:
        query = key.extract_keyword(prompt)
    return query