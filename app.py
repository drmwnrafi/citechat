import torch
from langchain.memory import ConversationBufferWindowMemory
import os
from tkinter import Tk, filedialog
import modules.vectorstore as vs
import modules.utils as utils
import modules.llms as llms
import ast
import gradio as gr
import warnings
import yaml


warnings.filterwarnings('ignore', category = UserWarning, module = 'gradio')

with open(os.path.join(os.getcwd(), "config.yaml"), "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

path   = None
vector_db = None
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
      source = document.metadata.get('source', 'N/A')
      page = document.metadata.get('page', 'N/A')
      bot_message += f"- {source}, **page:** {page}\n"
  else : 
     bot_message = llm(message)
  history.append((message, bot_message)) 
  return "", history

title_md = '# <p align="center">💬 CiteChat</p>'

desc = f"CiteChat is an innovative research assistant application designed to simplify the academic journey. By turning PDF documents into a treasure trove of knowledge. CiteChat functions as a dynamic chatbot, researchers simply upload a PDF and ask questions about the PDF. CiteChat by default, uses internet-connected BARD or locally run LLAMA2 to get responses. With CiteChat, I hope your research becomes more accessible and efficient than ever before." 

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
   
      chatbot = gr.Chatbot(avatar_images=(os.path.join(os.getcwd(), "logos", "user_logo.svg"), os.path.join(os.getcwd(), "logos", "logo.svg")),
                         bubble_full_width=False,show_copy_button=True, height=600)
      with gr.Row():
        msg = gr.Textbox(scale=99,
                          container=False,
                          placeholder="Prompt",
                          show_label=False,)
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        with gr.Column(scale=1):
          butt = gr.Button("Sent 📤", size="lg")
          clear = gr.ClearButton([msg, chatbot], value="Clear 🗑️", variant="primary",size="lg")
          butt.click(respond, [msg, chatbot], [msg, chatbot])

    with gr.Tab("Literature Search"):
       gr.Textbox("COMING SOON...",show_label=False, container=False)

if __name__=="__main__":
  try:
    demo.launch(favicon_path=os.path.join(os.getcwd(), "logos", "icon.ico"))
  except KeyboardInterrupt:
    demo.clear()
    demo.close()
  except Exception as e:
    demo.clear()
    demo.close()