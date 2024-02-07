import os
import os.path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import scoring

base_url = "https://pureportal.coventry.ac.uk/en/organisations/centre-for-health-and-life-sciences"
index_path = "indexdir"

def gather_and_store():
    # Fetch the page containing the list of publications
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize Whoosh index
    schema = Schema(title=TEXT(stored=True), authors=TEXT(stored=True), year=ID(stored=True), 
                    publication_url=ID(stored=True, unique=True), author_profile_url=ID(stored=True))
    
    if not os.path.exists(index_path):
        os.mkdir(index_path)
        
    ix = create_in(index_path, schema)
    writer = ix.writer()

    # Extract publication information
    results = []
    for publication_div in soup.find_all('div', class_='result-container'):
        title_tag = publication_div.find('h3', class_="title")
        title = title_tag.get_text(strip = True) if title_tag else "N/A"
        
        authors_tags = publication_div.find_all('a', class_='link person')
        authors = [author.text.strip() for author in authors_tags] if authors_tags else ["N/A"]

        year_tag = publication_div.find('span', class_='date')
        year = year_tag.text.strip() if year_tag else "N/A"

        publication_url_tag = publication_div.find('a', class_='link')
        publication_url = urljoin(base_url, publication_url_tag['href']) if publication_url_tag else "N/A"

        author_profile_url_tag = publication_div.find('a', class_='link person')
        author_profile_url = urljoin(base_url, author_profile_url_tag['href']) if author_profile_url_tag else "N/A"
        
        # Add data to the Whoosh index
        writer.add_document(title=title, authors=', '.join(authors), year=year,
                            publication_url=publication_url, author_profile_url=author_profile_url)
        
        results.append({
            'title': title,
            'authors': ', '.join(authors),
            'year': year,
            'publication_url': publication_url,
            'author_profile_url': author_profile_url
        })

    writer.commit()
    return results

def search_publications(query):
    ix = open_dir(index_path)
    final_results = []
    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        query_parser = MultifieldParser(["title", "authors"], ix.schema)
        query = query_parser.parse(query)
        results = searcher.search(query, terms=True)
        for result in results:
            final_results.append({
                "title": result['title'],
                "authors": result['authors'],
                "year": result['year'],
                "publication_url": result['publication_url'],
                "profile_url": result['author_profile_url'],
            })

    return final_results