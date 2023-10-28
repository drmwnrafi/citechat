from bs4 import BeautifulSoup
import requests, lxml, os, json
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pickle

options = Options()
# options.add_argument("--headless")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)


try:
    url = "https://www.google.com/scholar?q=dinov2&hl=en"
    driver.get(url)
    time.sleep(15)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    scholar_results = []
    for result in soup.select('.gs_r.gs_or.gs_scl'):
        title = result.select_one('.gs_rt').text
        snippet = result.select_one('.gs_rs').text
        id = result['data-cid']
        try:
            pdf_link = result.select_one('.gs_or_ggsm a:nth-child(1)')['href']
        except:
            pdf_link = None
    
        citation_info = f"https://scholar.google.com/scholar?q=info:{id}:scholar.google.com&output=cite"
        driver.get(citation_info)
        soup_cite = BeautifulSoup(driver.page_source, 'html.parser')
        cite = []
        for element in soup_cite.select("#gs_citt tr"):
            style_cite = element.select_one(".gs_cith").text.strip()
            content = element.select_one(".gs_citr").text.strip()
            cite.append({
                "cite_style" : style_cite,
                "cite_content" : content, 
            })
        ref_links = []
        for el in soup_cite.select("#gs_citi .gs_citi"):
            ref_links.append({
                "ref_format": el.text.strip(),
                "link": el.get("href")
            })
        scholar_results.append({
            'title': title,
            'snippet': snippet,
            'id': id,
            'pdf_link': pdf_link,
            'cite_content': cite,
            'reference_link': ref_links,
        })
    print(json.dumps(scholar_results, indent=2, ensure_ascii=False))
except Exception as e:
    print(e)



