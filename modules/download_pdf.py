import requests
import os

params = {
    'switchLocale': 'y',
    'siteEntryPassthrough': 'true'
}

def pdf_from_url(url:str, dir_path:str, filename:str):
    """
    params:
    url = link for pdf (it should .pdf)
    dir_path = directory for output
    filename = name of output
    """
    filename = filename.strip().replace(" ", "_")
    os.makedirs(dir_path, exist_ok=True)
    path = str(os.path.join(f"{dir_path}", filename))
    path = os.path.normpath(path)
    print("Downloading...")
    try :
        r = requests.get(url, params=params)
        with open(path, 'wb') as f:
            f.write(r.content)
    except :
        print("An error occurred while downloading")

