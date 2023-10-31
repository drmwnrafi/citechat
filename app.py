import torch
from langchain.memory import ConversationBufferWindowMemory
import ast
import os
from tkinter import Tk, filedialog
import modules.vectorstore as vs
import modules.utils as utils
import modules.llms as llms
import modules.search_papers as papers
import modules.bibtex_convert as convert
import gradio as gr
import warnings
import yaml
import modules.download_pdf as dload

warnings.filterwarnings('ignore', category = UserWarning, module = 'gradio')

with open(os.path.join(os.getcwd(), "config.yaml"), "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

path   = None
vector_db = None
list_msg = []
pdf_out = []
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=2, output_key='answer')

llm = llms.lang_model(model_name='google bard')

def on_browse(data_type):
    global path
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    if data_type == "Files":
        filenames = filedialog.askopenfilenames()
        root.destroy()
        if len(filenames) > 0:
            path = [str(file) for file in filenames]
        else:
            path = "Files not selected"


    elif data_type == "Folder":
        filename = filedialog.askdirectory()
        root.destroy()
        if filename:
            if os.path.isdir(filename):
                path = str(filename)
            else:
                path = "Invalid folder selected"

        else:
             path = "Folder not selected"
    return path

def create_vdb(path):
  global vector_db
  embeddings = vs.load_embeddings(config.get("embeddings"))

  if len(path)>1 and path != "." and path[0] == '[':
    path = ast.literal_eval(path)
    if isinstance(path, list):
        path = [os.path.normpath(file) for file in path]
  else:
        path = os.path.normpath(path)
  vector_db = vs.add_docs(path, embeddings)
  return {info_textbox: gr.update(value="Success")}

def options(acc, large_lang):
    global llm
    device = acc.lower()
    large_lang = large_lang.lower()
    if device == 'cuda':
        if torch.cuda.is_available():
            device = 'cuda'
            llm = llms.lang_model(device=device, model_name=large_lang)
            return {error_box: gr.update(value=f"Running {large_lang.upper()} on CUDA", visible=True)} 
        else :
            device = 'cpu'
            llm = llms.lang_model(device=device, model_name=large_lang)
            return {error_box: gr.update(value=f"CUDA is not available, running {large_lang.upper()} on CPU", visible=True)} 
    elif device == "cuda" or device == "cpu" and large_lang=='google bard':
       llm = llms.lang_model(model_name=large_lang)
       return {error_box: gr.update(value="Bard using internet connection, neither CPU nor CUDA", visible=True)}
    llm = llms.lang_model(device=device, model_name=large_lang)
    return {error_box: gr.update(value=f"Running {large_lang.upper()} on {device.upper()}", visible=True)}

def respond(message, history):
  global llm, vector_db
  if vector_db is not None:
    llm_dqa = utils.setup_dbqa(llm, vector_db, memory)
    output = llm_dqa({'question': message})
    bot_message = output['answer'] + "\n\n**Source :**\n"
    for document in output['source_documents']:
      try :
          source = convert.format_APA(document.metadata['source'])
          pdf = document.metadata['pdf_link']
          if pdf == 'None':
             bot_message += f"- {source}\n"
          else :
            bot_message += f"- {source}\n **PDF : {pdf}**\n"
      except :
          source = document.metadata.get('source', 'N/A')
          page = document.metadata.get('page', 'N/A')
          if source is not None and page is not None:
            bot_message += f"- {source}, **page:** {page}\n"
          else :
            bot_message += f"- {source}\n"
  else : 
     bot_message = llm(message)
  history.append((message, bot_message)) 
  return "", history

def respond_literature(message, history):
  global llm, vector_db, pdf_out, filenames
  query = utils.get_query_search(message)
  papers_content = papers.push_to_documents(query)
  embeddings = vs.load_embeddings(config.get("embeddings"))
  vector_db = vs.add_list_docs(papers_content, embeddings)
  if vector_db is not None:
    llm_dqa = utils.setup_dbqa(llm, vector_db, memory)
    output = llm_dqa({'question': message})
    bot_message = output['answer'] + "\n\n**Source :**\n"
    for document in output['source_documents']:
      try :
          source, title = convert.format_APA(document.metadata['source'])
          pdf_link = document.metadata['pdf_link']
          pdf_out.append({'link' : pdf_link, 'name' : title})
          if pdf_link == 'None':
             bot_message += f"- {source}\n"
          else :
            bot_message += f"- {source}\n **PDF : {pdf_link}**\n"
      except :
          source = document.metadata.get('source', 'N/A')
          page = document.metadata.get('page', 'N/A')
          if source is not None and page is not None:
            bot_message += f"- {source}, **page:** {page}\n"
          else :
            bot_message += f"- {source}\n"
    history.append((message, bot_message)) 
    return "", history

def vote(data: gr.LikeData, msg):
  global list_msg, pdf_out
  dir_path = os.path.join(os.getcwd(), "pdfs")
  embeddings = vs.load_embeddings(config.get("embeddings"))
  if data.liked and msg not in list_msg:
    list_msg.append(msg)
    pdf_out = [item for item in pdf_out if item['link'] != 'None']
    for pdf in pdf_out:
      dload.pdf_from_url(pdf['link'], dir_path, pdf['name'][:-1]+".pdf")
    vs.add_docs(dir_path, embeddings)
    pdf_out = []
    return "PDF downloaded and push to vectorstore"
  else :
    return "Do nothing 😛"

title_md = '# <p align="center">💬 CiteChat</p>'
desc = f"⚠️ Info : \n - If you push multiple PDFs, it may take a while to process and push to vectorstore. \n - If you want to run Literature Search feature, make sure you have Google Chrome installed.\n- If you select Google Bard as LLM, make sure you have an internet connection." 
theme = gr.themes.Soft(primary_hue='gray', secondary_hue = 'gray', font=[gr.themes.GoogleFont("Montserrat"), "ui-sans-serif", "sans-serif"])

with gr.Blocks(title="CiteChat", theme=theme) as demo:
    
    gr.Markdown(title_md)
    with gr.Row():
      gr.Textbox(desc,show_label=False, scale=99)
      dark_mode_btn = gr.Button(scale=1, value="🌓 Dark Toggle", variant="primary", size="sm")
      dark_mode_btn.click(
                None,
                None,
                None,
                _js="""() => {
                if (document.querySelectorAll('.dark').length) {
                    document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
                } else {
                    document.querySelector('body').classList.add('dark');
                }
            }""",
                api_name=False,
            )

    with gr.Row(equal_height=False):
      with gr.Accordion(open=False, label="Options"):
        with gr.Column():
          acc = gr.Dropdown(["CPU", "CUDA"], filterable=False, label="Accelerator", info="Choose the accelerator :")
          large_lang = gr.Dropdown(["Google Bard", "Llama 2"], filterable=False, label="LLM", info="Select the LLM variant you'd like to utilize :")
          error_box = gr.Textbox(visible=False, label="Error Message")
          done_options = gr.Button("Done", size="lg", variant="primary")
          done_options.click(fn = options, inputs = [acc, large_lang], outputs = [error_box])
      
    with gr.Tab("Local Papers"):
      with gr.Row(variant='panel', equal_height=True):
        with gr.Column(scale=97):
          data_type = gr.Radio(choices=["Files", "Folder"], value="Files", label="Select Files or Directory")
          input_path = gr.Textbox(label="Selected Files or Directory", interactive=False)
        with gr.Column(scale=3):
          image_browse_btn = gr.Button("Browse",size="sm")
          done_vectorstr_btn = gr.Button("Done", size="sm")
          info_textbox = gr.Textbox(visible=True, value="Click Done", label="Infomation Message", info="If you send a request without pressing 'Done', then you are using Base LLM")
          image_browse_btn.click(on_browse, inputs=data_type, outputs=input_path, show_progress="hidden")
          done_vectorstr_btn.click(create_vdb, inputs=input_path, outputs=info_textbox)
   
      chatbot = gr.Chatbot(label="Local Papers", avatar_images=(os.path.join(os.getcwd(), "logos", "user_logo.png"), os.path.join(os.getcwd(), "logos", "logo.png")),
                         bubble_full_width=False,show_copy_button=True, height=600)
      with gr.Row():
        msg = gr.Textbox(scale=99,
                          container=False,
                          placeholder="Prompt",
                          show_label=False,)
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        with gr.Column(scale=1):
          button_send = gr.Button("Sent 📤", size="lg")
          clear = gr.ClearButton([msg, chatbot], value="Clear 🗑️", variant="primary",size="lg")
          button_send.click(respond, [msg, chatbot], [msg, chatbot])

    with gr.Tab("Literature Search"):
      literature_info = gr.Textbox(label="Proccess Info", info = "👍🏻 Like : Push PDF reference to vectorstore 👎🏻 Dislike : Do nothing")
      chatbot_literature = gr.Chatbot(label = "Literature Search", avatar_images=(os.path.join(os.getcwd(), "logos", "user_logo.png"), os.path.join(os.getcwd(), "logos", "logo.png")),
                         bubble_full_width=False,show_copy_button=True, height=600)
      with gr.Row():
        msg_literature = gr.Textbox(scale=99,
                          container=False,
                          placeholder="Prompt",
                          show_label=False,)
        msg_literature.submit(respond_literature, [msg_literature, chatbot_literature], [msg_literature, chatbot_literature])
        chatbot_literature.like(vote, inputs=[msg_literature], outputs=[literature_info])
        with gr.Column(scale=1):
          button_literature = gr.Button("Sent 📤", size="lg")
          clear_literature = gr.ClearButton([msg_literature, chatbot_literature], value="Clear 🗑️", variant="primary",size="lg")
          button_literature.click(respond_literature, [msg_literature, chatbot_literature], [msg_literature, chatbot_literature])

if __name__=="__main__":
  try:
    demo.launch(favicon_path=os.path.join(os.getcwd(), "logos", "logo.ico"), 
                # inbrowser = True
                )
  except KeyboardInterrupt:
    demo.clear()
    demo.close()
  except Exception as e:
    demo.clear()
    demo.close()