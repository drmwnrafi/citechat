
# 💬 CiteChat
<div align="center">
  <img src="https://github.com/drmwnrafi/citechat/raw/main/logos/logo.svg" alt="Logo" width="200">
</div>
CiteChat is an research assistant web app designed to simplify the academic journey. By turning PDF documents into a treasure trove of knowledge. CiteChat functions as a chatbot, researchers simply upload a PDF and ask questions about the PDF. CiteChat by default, uses internet-connected BARD or locally (optional) run LLAMA-2 to get responses. With CiteChat, I hope your research becomes more accessible and efficient than ever before.

<div align="center">
  <img src="https://github.com/drmwnrafi/citechat/blob/main/logos/flow.svg" alt="Logo" width="500">
</div>

## Installation

Install all library using `poetry`
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
poetry run python app.py
```
`CTRL + C` in your terminal to close the app and the port
## How to get Bard tokens
1. Go to [Google Bard](https://bard.google.com/chat)
2. Right click, click __Inspect__ or `Ctrl + Shift + C`
3. Click `>>` symbol and select `Application`
4. Search `__Secure-1PSID` and copy to `config.yaml` all the tokens you need
    
## Acknowledgements

 - [BardAPI](https://github.com/dsdanielpark/Bard-API)

