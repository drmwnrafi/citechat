import re

italic_start = "<em>"
italic_end = "</em>"

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
    authors = f"{', '.join(authors[:-1])}, & {authors[-1]}" if len(authors)>1 else f"{authors[0]}"
    title = f" {title_match.group(1)}." if title_match is not None else ''
    journal = f" {journal_match.group(1)}," if journal_match is not None and volume_match is not None else (f" {journal_match.group(1)}." if journal_match is not None else '')
    year = f" ({year_match.group(1)})." if year_match is not None else ' (n.d).'
    volume = f" {volume_match.group(1)}." if volume_match is not None else ''
    
    formatted_citation = f"{authors}{year}{title}{italic_start}{journal}{volume}{italic_end}"
    return formatted_citation, title