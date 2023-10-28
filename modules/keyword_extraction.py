import nltk
import os
import sys
from rake_nltk import Rake

if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    directory = sys.prefix
else :
    directory = os.path.expanduser("~")

sw_path = os.path.normpath(os.path.join(directory,"nltk_data"))
punkt_path = os.path.normpath(os.path.join(directory,"nltk_data"))

if nltk.data.find(sw_path) and nltk.data.find(punkt_path):
    pass
else:
    nltk.download('stopwords', download_dir=sw_path)
    nltk.download('punkt', download_dir=punkt_path)

rake_nltk_var = Rake()

def extract_keyword(text:str):
    """
    params:
    text:str = query to extract the keywords

    return str
    """
    rake_nltk_var.extract_keywords_from_text(text)
    keyword_extracted = rake_nltk_var.get_ranked_phrases()
    return " AND ".join(keyword_extracted)
