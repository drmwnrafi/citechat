import os
from bardapi import Bard
from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from huggingface_hub import hf_hub_download
from langchain.llms.base import LLM
from langchain.llms import CTransformers
from huggingface_hub import hf_hub_download
from bardapi import BardCookies

os.environ['_BARD_API_KEY'] = "xxxxxxxx"

class BardLLM(LLM):
    @property
    def _llm_type(self) -> str:
       return "Bard"
    
    def _call(self, prompt:str, stop:Optional[List[str]]=None, run_manager:Optional[CallbackManagerForLLMRun]=None,**kwargs: Any) -> str:
        response = Bard().get_answer(prompt)['content']
        return response
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying params"""
        return {}
   

def lang_model(model_name:str=None):
    if model_name.lower() == 'google bard':
        llm = BardLLM()

    elif model_name.lower() == 'llama 2':
        try :
            path = hf_hub_download(repo_id="TheBloke/Llama-2-7B-Chat-GGML", filename="llama-2-7b-chat.ggmlv3.q2_K.bin")
            llm = CTransformers(model=path, model_type='llama', config={'max_new_tokens': 150, 'temperature': 0.01})
        except :
            llm = CTransformers(model="TheBloke/Llama-2-7B-Chat-GGML", 
                               model_file="llama-2-7b-chat.ggmlv3.q2_K.bin",
                               model_type='llama', 
                               config={'max_new_tokens': 150, 'temperature': 0.01})
        
    elif model_name.lower() == 'mistral':
        try :
            path = hf_hub_download(repo_id="TheBloke/Mistral-7B-v0.1-GGUF", filename="mistral-7b-v0.1.Q2_K.gguf")
            llm = CTransformers(model=path, model_type='mistral', config={'max_new_tokens': 150, 'temperature': 0.01})
        except :
            llm = CTransformers(model="TheBloke/Mistral-7B-v0.1-GGUF", 
                                model_file="mistral-7b-v0.1.Q2_K.gguf", 
                                model_type='mistral', 
                                config={'max_new_tokens': 150, 'temperature': 0.01})
    return llm