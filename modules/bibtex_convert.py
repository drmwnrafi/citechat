import re

italic_start = "\033[3m"
italic_end = "\033[0m"

def format_IEEE(bibtex:str):
    """
    bibtex:str = bibtext in str dtype
    return IEEE style formated in str
    """
    author_match = re.search(r'author=\{(.+?)\}', bibtex)
    title_match = re.search(r'title=\{(.+?)\}', bibtex)
    journal_match = re.search(r'journal=\{(.+?)\}', bibtex) or re.search(r'booktitle=\{(.+?)\}', bibtex)
    year_match = re.search(r'year=\{(\d{4})\}', bibtex)
    volume_match = re.search(r'volume=\{(.+?)\}', bibtex)
    authors = author_match.group(1).split(' and ')
    authors = [f'{author.split()[0][0]}. {author.split()[-1]}' for author in authors]
    title = title_match.group(1)
    journal = journal_match.group(1)
    year = year_match.group(1)
    if volume_match != None:
        volume = volume_match.group(1)
        formatted_citation = f"{', '.join(authors[:-1])}, and {authors[-1]}, '{title}', {italic_start}{journal}{italic_end}, vol. {volume}, {year}."
    else :
        formatted_citation = f"{', '.join(authors[:-1])}, and {authors[-1]}, '{title}', {italic_start}{journal}{italic_end}, {year}."
    
    return formatted_citation

def format_APA(bibtex:str):
    """
    bibtex:str = bibtext in str dtype
    return APA Style formated in str
    """
    author_match = re.search(r'author=\{(.+?)\}', bibtex)
    title_match = re.search(r'title=\{(.+?)\}', bibtex)
    journal_match = re.search(r'journal=\{(.+?)\}', bibtex) or re.search(r'booktitle=\{(.+?)\}', bibtex)
    year_match = re.search(r'year=\{(\d{4})\}', bibtex)
    volume_match = re.search(r'volume=\{(.+?)\}', bibtex)
    authors = author_match.group(1).split(' and ')
    authors = [f'{author.split()[-1]}, {author.split()[0][0]}.' for author in authors]
    title = title_match.group(1)
    # journal = journal_match.group(1)
    year = year_match.group(1)
    # if volume_match != None:
    #     volume = volume_match.group(1)
    #     formatted_citation = f"{', '.join(authors[:-1])}, & {authors[-1]} ({year}). {title}."
    # else :
        
    formatted_citation = f"{', '.join(authors[:-1])}, & {authors[-1]} ({year}). {title}."
    return formatted_citation

def format_MLA(bibtex:str):
    """
    bibtex:str = bibtext in str dtype
    return MLA Style formated in str
    """
    author_match = re.search(r'author=\{(.+?)\}', bibtex)
    title_match = re.search(r'title=\{(.+?)\}', bibtex)
    journal_match = re.search(r'journal=\{(.+?)\}', bibtex) or re.search(r'booktitle=\{(.+?)\}', bibtex)
    year_match = re.search(r'year=\{(\d{4})\}', bibtex)
    volume_match = re.search(r'volume=\{(.+?)\}', bibtex)
    authors = author_match.group(1).split(' and ')
    authors = [f'{author.split()[-1]}, {author.split()[0]}' for author in authors]
    if len(authors) > 1:
        authors = authors[0]
        authors = f"{authors} et al."
    else:
        authors = authors[0]
    title = title_match.group(1)
    journal = journal_match.group(1)
    year = year_match.group(1)
    if volume_match != None:
        volume = volume_match.group(1)
        formatted_citation = f'{authors} "{title}". {italic_start}{journal} preprint {journal}:{volume}{italic_end} ({year}).'
    else :
        formatted_citation = f'{authors} "{title}". {italic_start}{journal}{italic_end} ({year}).'

    return formatted_citation
