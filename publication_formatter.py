class PublicationFormatter:
    def format_publication(self, publication, affiliation):
        title = publication['title']
        journal = publication['journal']
        authors_with_affiliations = [publication['authors'][i] for i, aff in enumerate(publication['affiliations']) if affiliation in aff[0]]
        
        return f"📚 {title}\n📝 Journal: {journal}\n🔬 Affiliated Authors: {', '.join(authors_with_affiliations)}"