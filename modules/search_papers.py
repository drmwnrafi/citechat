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
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    query = query.replace(' ', '+')
    if first_year == None or last_year == None :
        url = f"https://www.semanticscholar.org/search?q={query}&sort=relevance"
    else :
        url = f"https://www.semanticscholar.org/search?year%5B0%5D={str(last_year)}&year%5B1%5D={str(first_year)}&q={query}&sort=relevance&pdf=true"
    
    driver.get(url)
    time.sleep(3)
    for count in range(1, 3):
        try:
            driver.execute_script(f'document.querySelector("#main-content > div.flex-item.flex-item--width-66.flex-item__left-column > div.result-page > div:nth-child({count}) > div.tldr-abstract-replacement.text-truncator > button").click()')
        except :
            driver.execute_script(f'document.querySelector("#main-content > div.flex-item.flex-item--width-66.flex-item__left-column > div.result-page > div:nth-child({count}) > div.cl-paper-abstract > span > button").click()')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    results = soup.select(".cl-paper-row.serp-papers__paper-row.paper-v2-cue.paper-row-normal")
    scholar_results = []

    if len(results) > 2:
        for_loop = results[:2]
    elif len(results)< 2:
        for_loop = results 

    for result in for_loop:    
        # title = result.select_one(".cl-paper-title").text

        try:
            pdf_link = result.find("div", class_ ="flex-row paper-badge-list").find('a')['href']
        except:
            pdf_link = 'None'
        
        try:
            overview = result.find("div", class_="cl-paper-abstract").text.replace('TLDR', '').replace('Collapse', '')
        except :
            overview = result.find("div", class_="tldr-abstract-replacement text-truncator").text.replace('TLDR', '').replace('Collapse', '')
        
        cite_button = driver.find_element("xpath","//button[contains(., 'Cite')]")
        driver.execute_script("arguments[0].click();", cite_button)

        soup_cite = BeautifulSoup(driver.page_source, 'html.parser')

        bibtex_str = soup_cite.find('cite', class_='formatted-citation--style-bibtex').text.strip()
    
        scholar_results.append({
            "abstract" : overview if overview is not None else 'None',
            "pdf" : pdf_link,
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
            "abstract": result.summary,
            "pdf" : result.pdf_url,
            "bibtex": f'''@article{{{{
                title={{{result.title}}},
                author={{{authors_string}}},
                year={{{result.published.year}}},
                url={{{result.pdf_url}}},
                journal={{arXiv}}}}}}'''
        })
    return results

def push_to_documents(query):
    try:
        results = semanticscholars_search(query)
    except :
        results = arxiv_search(query)

    output = []
    
    for i in range(len(results)):
        output.append(Document(page_content=results[i]['abstract'], metadata=dict(source = results[i]['bibtex'])))
    return output
