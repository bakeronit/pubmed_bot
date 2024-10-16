import requests
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)

class PubmedScraper:
    def __init__(self):
        self.PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    def get_pmids_by_affiliation(self, affiliation):
        """Fetches PMIDs for publications from the last week based on the given affiliation."""
        one_week_ago = (datetime.now() - timedelta(weeks=1)).strftime("%Y/%m/%d")
        today = datetime.now().strftime("%Y/%m/%d")
        params = {
            "db": "pubmed",
            "term": f"{affiliation}[Affiliation]",
            "retmax": 100,
            "retmode": "json",
            "sort": "pubdate",
            "datetype": "pdat",
            "mindate": one_week_ago,
            "maxdate": today
        }

        try:
            response = requests.get(self.PUBMED_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()  # Raises an error for bad status codes
            pubmed_ids = response.json()["esearchresult"]["idlist"]
            logging.info(f"Successfully fetched {len(pubmed_ids)} PMIDs for {affiliation}")
            return pubmed_ids
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch PMIDs: {e}")
            return []

    def get_title_and_affiliation(self, pmid, max_retries=3, initial_delay=1):
        """Fetches the title and affiliations for a given PMID."""
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                response = requests.get(self.PUBMED_FETCH_URL, params=params, timeout=20)
                response.raise_for_status()
                root = ET.fromstring(response.content)
                journal = root.find(".//Journal/Title").text
                title = root.find(".//ArticleTitle").text
                abstract = root.find(".//AbstractText")
                affiliations = [aff.text for aff in root.findall(".//AffiliationInfo/Affiliation")]
                authors = root.findall(".//Author")
                valid_authors = []
                valid_affiliations = []
                for item, author in enumerate(authors):
                    if item == 0 or item == len(authors) - 1 or author.attrib.get('EqualContrib', None) == 'Y':
                        valid_authors.append(self._get_author_name(author))
                        # Get the affiliation for the author
                        if author.find('AffiliationInfo') is not None:
                            author_affiliations = [aff.text for aff in author.findall('AffiliationInfo/Affiliation')]
                            valid_affiliations.append(author_affiliations)
                return journal, title, [valid_authors, valid_affiliations], abstract
            except requests.exceptions.RequestException as e:
                logging.warning(f"Failed to fetch details for PMID {pmid}: {e}")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"Failed to fetch details for PMID {pmid}: {e}")
            if attempt < max_retries:
                logging.warning(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
    
        logging.error(f"Failed to fetch details for PMID {pmid} after {max_retries} attempts.")
        return None, None, [[],[]], None

    def _get_author_name(self, author):
        last_name = author.find('LastName').text if author.find('LastName') is not None else ''
        first_name = author.find('ForeName').text if author.find('ForeName') is not None else ''
        return f"{last_name}, {first_name}"

    def process_publication(self, pmid, affiliation):
        """Processes publications for the given affiliation."""
        journal, title, [valid_authors, valid_affiliations], abstract = self.get_title_and_affiliation(pmid)
        if valid_affiliations and any(affiliation.lower() in aff[0].lower() for aff in valid_affiliations):
            publication = {
                "pmid": pmid,
                "journal": journal,
                "title": title,
                "authors": valid_authors,
                "affiliations": valid_affiliations,
                "abstract": abstract.text if abstract is not None else ""
            }
            return publication
        return None

    def print_publication(self, publication):
        """Prints the publication details."""
        if not publication:
            return
        print("------------------------------------------------------------")
        print(f"Title: {publication['title']} | PMID: {publication['pmid']}")
        print(f"Journal: {publication['journal']}")
        for author, affiliations in zip(publication['authors'], publication['affiliations']):
            if affiliation in affiliations[0]:
                print(f"- {author}: {', '.join(affiliations)}")
        print(f"Abstract: {publication['abstract']}")
        print("------------------------------------------------------------")

if __name__ == "__main__":
    affiliation = "QIMR Berghofer Medical Research Institute"
    pubmed_scraper = PubmedScraper()
    pmids = pubmed_scraper.get_pmids_by_affiliation(affiliation)
    num_publications = 0
    for pmid in pmids:
        publication = pubmed_scraper.process_publication(pmid, affiliation)
        if publication:
            num_publications += 1
        pubmed_scraper.print_publication(publication)
    print(f"Total publications: {num_publications}")
