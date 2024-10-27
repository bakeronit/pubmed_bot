from pubmed_scrapper import PubmedScraper
from publication_formatter import PublicationFormatter
import yagmail
import os

class PubmedTracker:
    def __init__(self, affiliation):
        self.pubmed_scraper = PubmedScraper()
        self.formatter = PublicationFormatter()
        self.affiliation = affiliation
        self.publications = self.get_publications()
    
    def get_publications(self):
        pmids = self.pubmed_scraper.search_pmids_by_affiliation(self.affiliation)
        publications = []
        for pmid in pmids:
            publication = self.pubmed_scraper.process_publication(pmid, self.affiliation)
            if publication:
                publications.append(publication)
        return publications

    def print(self):
        for publication in self.publications:
            print(self.formatter.format_publication(publication, self.affiliation))
            print("------------------------------------------------------------")
    #add to parameter to send email, to can be a single string or a list of strings
    def send_email(self, to: str|list[str]):
        ## use python dotenv to get the email and password
        PASSWORD = os.getenv("GMAIL_PASSWORD")
        GMAIL_USER = os.getenv("GMAIL_USER")
        contents = "------------\n".join([ self.formatter.format_publication(publication, self.affiliation) for publication in self.publications])
        print(contents)
        yag = yagmail.SMTP(GMAIL_USER, PASSWORD)
        yag.send(to, 'Pubmed Publications', contents)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    emails = os.getenv("EMAILS")
    tracker = PubmedTracker(os.getenv("AFFILIATION"))
    tracker.print()
    tracker.send_email(emails)

