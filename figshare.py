import requests
from toolz import merge

from scrape import get_text_for_url_safe


FIGSHARE_DOCUMENT_URL = 'https://api.figshare.com/v2/articles'


# Exception classes specific to figshare API

class EntityNotFound(ValueError):
    def __init__(self, url):
        super(ValueError, self).__init__(
            'entity not found for URL: {}'.format(url)
        )


class FigshareArticle:
    def __init__(self, id, url, title, keywords, authors, license, summary,
                 categories, documents, original_article):
        self.id = id
        self.url = url
        self.title = title
        self.keywords = keywords
        self.authors = authors
        self.license = license
        self.summary = summary
        self.categories = categories
        self.documents = documents
        self.original_article = original_article

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'keywords': self.keywords,
            'authors': self.authors,
            'license': self.license,
            'summary': self.summary,
            'categories': self.categories,
            'documents': self.documents,
            'original_article': self.original_article
        }

    @staticmethod
    def from_url(url, tika_rest_url):
        d = requests.get(url).json()
        if 'code' in d and d['code'] == 'EntityNotFound':
            raise EntityNotFound(url)

        return FigshareArticle(
            id=d['id'],
            url=url,
            title=d['title'],
            keywords=d['tags'],
            authors=[author['full_name'] for author in d['authors']],
            license=d['license']['name'],
            summary=d['description'],
            categories=[category['title'] for category in d['categories']],
            documents=[
                merge(
                    get_text_for_url_safe(f['download_url'], tika_rest_url),
                    {
                        'url': f['download_url'],
                        'title': None  # for compatibility with sharekit output
                    }
                )
                for f in d['files']
            ],
            original_article=d
        )
