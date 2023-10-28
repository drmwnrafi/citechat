from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import arxiv
from langchain.schema import Document

def semanticscholars_search(query, first_year = None, last_year=None):
    options = Options()
    # options.add_argument("--headless")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    query = query.replace(' ', '+')
    if first_year == None or last_year == None :
        url = f"https://www.semanticscholar.org/search?q={query}&sort=relevance"
    else :
        url = f"https://www.semanticscholar.org/search?year%5B0%5D={str(last_year)}&year%5B1%5D={str(first_year)}&q={query}&sort=relevance&pdf=true"
    
    driver.get(url)
    time.sleep(2)

    for count in range(1, 3):
        try:
            driver.execute_script(f'document.querySelector("#main-content > div.flex-item.flex-item--width-66.flex-item__left-column > div.result-page > div:nth-child({count}) > div.tldr-abstract-replacement.text-truncator > button").click()')
        except :
            driver.execute_script(f'document.querySelector("#main-content > div.flex-item.flex-item--width-66.flex-item__left-column > div.result-page > div:nth-child({count}) > div.cl-paper-abstract > span > button").click()')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    results = soup.select(".cl-paper-row.serp-papers__paper-row.paper-v2-cue.paper-row-normal")
    scholar_results = []
    
    for result in results[:2]:    
        title = result.select_one(".cl-paper-title").text
        
        try:
            overview = result.find("div", class_="cl-paper-abstract").text.replace('TLDR', '').replace('Collapse', '')
        except :
            overview = result.find("div", class_="tldr-abstract-replacement text-truncator").text.replace('TLDR', '').replace('Collapse', '')
        
        try:
            pdf_link = result.select_one(".flex-row.paper-badge-list a")['href']
        except:
            pdf_link = 'None'
        
        cite_button = driver.find_element("xpath","//button[contains(., 'Cite')]")
        driver.execute_script("arguments[0].click();", cite_button)

        soup_cite = BeautifulSoup(driver.page_source, 'html.parser')

        bibtex_str = soup_cite.find('cite', class_='formatted-citation--style-bibtex').text.strip()
    
        scholar_results.append({
            "title" : title if title is not None else 'None',
            "abstract" : overview if overview is not None else 'None',
            "pdf" : pdf_link if pdf_link is not None else 'None',
            "bibtex" : bibtex_str if bibtex_str is not None else 'None',
        })
    
    return scholar_results

def arxiv_search(query):
    search = arxiv.Search(
       query = query,
       max_results = 2,
       sort_by = arxiv.SortCriterion.Relevance,
       )
    
    results=[]
    for result in search.results():
        author_names = [author.name for author in result.authors]
        authors_string = ' and '.join(author_names)

        results.append({
            "summary": result.summary,
            "bibtex": f'''@article{{{{
                title={{{result.title}}},
                author={{{authors_string}}},
                year={{{result.published.year}}},
                url={{{result.pdf_url}}},
                journal={{arXiv}}
            }}}}'''
        })
    return results

def push_to_documents(query, num_references:int = 2):
    semantics_results = semanticscholars_search(query)
    arxiv_results = arxiv_search(query)
    ss = []
    axv = []
    
    for i in range(num_references):
        ss.append(Document(page_content=semantics_results[i]['abstract'], metadata=dict(source = semantics_results[i]['bibtex'])))
        axv.append(Document(page_content=arxiv_results[i]['summary'], metadata=dict(source = arxiv_results[i]['bibtex'])))

    return ss, axv