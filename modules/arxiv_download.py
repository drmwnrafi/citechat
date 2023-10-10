import arxiv

def search_download(quest):
    search = arxiv.Search(
       query = quest,
       max_results = 3,
       sort_by = arxiv.SortCriterion.Relevance,
       )
    for result in search.results():
        print(result.title)