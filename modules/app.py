import torch
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferWindowMemory
import file_chunking as loader
import os
from tkinter import Tk, filedialog
import vectorstore as vs
import utils
import llms
import ast
import gradio as gr
import warnings

warnings.filterwarnings('ignore', category = UserWarning, module = 'gradio')
path   = None
vector_db = None
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=2, output_key='answer')
llm = llms.lang_model('google bard')

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
            path = ["Files not selected"]


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
  embeddings = vs.load_embeddings("sentence-transformers/all-MiniLM-L6-v2")

  if len(path)>1 and path != "." and path[0] == '[':
    path = ast.literal_eval(path)
    if isinstance(path, list):
        path = [os.path.normpath(file) for file in path]
  else:
        path = os.path.normpath(path)
  vector_db = vs.add_docs(path, embeddings)
  print(vector_db, type(vector_db))
  return {info_textbox: gr.update(value="Vectorstore has been created")}

def options(acc, large_lang):
    global llm
    device = acc.lower()
    large_lang = large_lang.lower()
    if device == 'cuda':
        if torch.cuda.is_available():
            device = 'cuda' 
        else :
            device = 'cpu'
        return {error_box: gr.update(value="CUDA is not available, running on CPU", visible=True)} 
    elif device == "cuda" or device == "cpu" and large_lang=='google bard':
       return {error_box: gr.update(value="Bard using internet connection, neither CPU nor CUDA", visible=True)}
       pass
    llm = llms.lang_model(model_name=large_lang)

def respond(message, history):
  global llm, vector_db
  llm_dqa = utils.setup_dbqa(llm, vector_db, memory)
  output = llm_dqa({'question': message})
  bot_message = output['answer'] + "\n\n**Source :**\n"
  for document in output['source_documents']:
    source = document.metadata.get('source', 'N/A')
    page = document.metadata.get('page', 'N/A')
    bot_message += f"- {source}, **page:** {page}\n"
  history.append((message, bot_message)) 
  return "", history

title_md = f"# ![]() CiteChat"

theme = gr.themes.Soft(primary_hue='gray', secondary_hue = 'gray', font=[gr.themes.GoogleFont("Montserrat"), "ui-sans-serif", "sans-serif"])

with gr.Blocks(title="CiteChat", theme=theme) as demo:
    
    gr.Markdown(title_md)
    with gr.Row(equal_height=False):
      with gr.Accordion(open=False, label="Options"):
        with gr.Column():
          acc = gr.Dropdown(["CPU", "CUDA"], label="Accelerator", info="Choose the accelerators : ")
          large_lang = gr.Dropdown(["Google Bard", "Llama 2", "Mistral"], label="LLM", info="Choose LLM you want to use : ")
          error_box = gr.Textbox(visible=False, label="Error Message")
          done_options = gr.Button("Done", size="lg", variant="primary")
          done_options.click(fn = options, inputs = [acc, large_lang], outputs = [error_box])
      
      dark_mode_btn = gr.Button(scale=1, value="Dark Mode", variant="primary", size="sm")
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
      
    with gr.Tab("Stored Papers"):
      with gr.Row(variant='panel', equal_height=False):
        with gr.Column(scale=9):
          data_type = gr.Radio(choices=["Files", "Folder"], value="Files", label="Select Files or Directory")
          input_path = gr.Textbox(label="Selected Files or Directory", interactive=False)
        with gr.Column(scale=3):
          image_browse_btn = gr.Button("Browse",size="sm")
          done_vectorstr_btn = gr.Button("Done and Create Vectorstore", size="sm")
          info_textbox = gr.Textbox(visible=True, value="Click Done", label="Info Message",)
          image_browse_btn.click(on_browse, inputs=data_type, outputs=input_path, show_progress="hidden")
          done_vectorstr_btn.click(create_vdb, inputs=input_path, outputs=info_textbox)

    with gr.Tab("Literature Search"):
       pass

    chatbot = gr.Chatbot(avatar_images=(os.path.join(os.getcwd(), "logos", "user_logo.svg"), os.path.join(os.getcwd(), "logos", "logo.svg")),
                         bubble_full_width=False,show_copy_button=True)

    with gr.Row():
      msg = gr.Textbox(scale=97,
                     container=False,
                     placeholder="Prompt",
                     show_label=False,)
      msg.submit(respond, [msg, chatbot], [msg, chatbot])
      with gr.Column(scale=3):
          butt = gr.Button("Sent 📤", size="lg")
          clear = gr.ClearButton([msg, chatbot], value="Clear 🗑️", variant="primary",size="lg")
          butt.click(respond, [msg, chatbot], [msg, chatbot])

if __name__=="__main__":
  try:
    demo.launch()
  except KeyboardInterrupt:
    demo.clear()
    demo.close()
  except Exception as e:
    demo.clear()
    demo.close()