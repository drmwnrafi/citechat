from bardapi import Bard
import requests
from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms import CTransformers
from huggingface_hub import hf_hub_download
from ctransformers import AutoModelForCausalLM
import yaml
import os

with open(os.path.join(os.getcwd(), "config.yaml"), "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

session = requests.Session()
session.cookies.set("__Secure-1PSID", config.get("__Secure-1PSID"))
session.cookies.set("__Secure-1PSIDCC", config.get("__Secure-1PSIDCC"))
session.cookies.set("__Secure-1PSIDTS", config.get("__Secure-1PSIDTS"))
session.headers = {
        "Host": "bard.google.com",
        "X-Same-Domain": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.4472.114 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://bard.google.com",
        "Referer": "https://bard.google.com/",
 }

token = config.get("__Secure-1PSID")

class BardLLM(LLM):
    @property
    def _llm_type(self) -> str:
       return "Bard"
    
    def _call(self, prompt:str, stop:Optional[List[str]]=None, run_manager:Optional[CallbackManagerForLLMRun]=None,**kwargs: Any) -> str:
        response = Bard(token=token, session=session, timeout=30).get_answer(prompt)['content']
        return response
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying params"""
        return {}

class CustomLLM(LLM):
    model:Any
    def __init__(self, model):
        super().__init__()
        self.model = model

    @property
    def _llm_type(self) -> str:
       return "custom"
    
    def _call(self, prompt:str, stop:Optional[List[str]]=None, run_manager:Optional[CallbackManagerForLLMRun]=None,**kwargs: Any) -> str:
        response = self.model(prompt)
        return response[len(prompt):]
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying params"""
        return {}


def lang_model(device:str='cpu',  model_name:str=None):
    if model_name.lower() == 'google bard':
        llm = BardLLM()

    elif model_name.lower() == 'llama 2':
        print(device, model_name)
        llm = custom_llm(repo_id=config.get("repo_id"), filename=config.get("model_file"), device = device)
        
    return llm

def custom_llm(repo_id=None, filename=None, device:str=None):
    try :
            path = hf_hub_download(repo_id=repo_id, filename=filename)
            if device == 'cpu':
                llm = CTransformers(model=path, model_type=filename.split("-")[0], config={'max_new_tokens': 150, 'temperature': 0.1})
            else :
                llm = AutoModelForCausalLM.from_pretrained(model_path_or_repo_id=path, gpu_layers=50)
                llm = CustomLLM(model=llm)
    except :
            if device == 'cpu':
                llm = CTransformers(model=repo_id, model_file=filename,
                                    model_type=filename.split("-")[0], 
                                    config={'max_new_tokens': 150, 'temperature': 0.1})
            else :
                llm = AutoModelForCausalLM.from_pretrained(model_path_or_repo_id=repo_id, model_file=filename, gpu_layers=50)
                llm = CustomLLM(model=llm)
    return llm
