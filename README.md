
# 💬 CiteChat
<div align="center">
  <img src="https://github.com/drmwnrafi/citechat/blob/main/logos/citechat_transparent.png" alt="Logo" width="800">
</div>
<br>
CiteChat is a helper for your academic journey, offering a unique and interactive approach to assisting with research. It turns PDF documents into knowledge resources and operates as a chatbot. Researchers can easily upload PDFs or search through Arxiv and SemanticScholar, then submit questions to CiteChat. By default, it uses an internet connection to Google Bard, but you also have the option of Llama-2 7B GGML (2 bits quantize) which can be run locally. With CiteChat, I hope your research becomes not only more accessible but also efficient.
<br>
<br>

<div align="center">
  <img src="https://github.com/drmwnrafi/citechat/blob/main/logos/flow.png" alt="Logo" width="700">
</div>
<br>

>If there's any error or bugs, feel free to [open a discussion](https://github.com/drmwnrafi/citechat/issues) to report them.

## Demo
![](https://github.com/drmwnrafi/citechat/blob/main/media/demo.gif)

## Installation

Install all library using `python venv`
```
 cd citechat
 pip install -r requirements.txt
```
Put BardAPI tokens on `config.yaml`, check [how to get Bard tokens](https://github.com/drmwnrafi/citechat#how-to-get-bard-tokens)
```
# Bard Tokens
__Secure-1PSID : "Put your token here"
__Secure-1PSIDCC : "Put your token here"
__Secure-1PSIDTS : "Put your token here"
```
To run the app
```
python app.py
```
`CTRL + C` in your terminal to close the app and the port

## How to get Bard tokens
![](https://github.com/drmwnrafi/citechat/blob/main/media/bard_cookies.gif)
1. Go to [Google Bard](https://bard.google.com/chat)
2. Right click, click __Inspect__ or `Ctrl + Shift + C`
3. Click `>>` symbol and select `Application`
4. Search `__Secure-1PSID` and copy to `config.yaml` all the tokens you need
    
## Acknowledgements

 - [BardAPI](https://github.com/dsdanielpark/Bard-API)
   
