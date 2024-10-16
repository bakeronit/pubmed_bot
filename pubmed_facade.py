from pubmed_scrapper import PubmedScraper
from publication_formatter import PublicationFormatter
import time

class PubmedFacade:
    def __init__(self):
        self.pubmed_scraper = PubmedScraper()
        self.formatter = PublicationFormatter()
        self.affiliation = "QIMR Berghofer Medical Research Institute"
    
    def run(self):
        pmids = self.pubmed_scraper.get_pmids_by_affiliation(self.affiliation)
        num_publications = 0
        for pmid in pmids:
            publication = self.pubmed_scraper.process_publication(pmid, self.affiliation)
            if publication:
                num_publications += 1
                print(self.formatter.format_publication(publication, self.affiliation))
                print("------------------------------------------------------------")
        print(f"Total publications: {num_publications}")

if __name__ == "__main__":
    PubmedFacade().run()