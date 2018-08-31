import requests


ALLOWED_CONTENT_TYPES = frozenset([
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
])


class IsYoutubeLink(Exception):
    def __init__(self, url):
        super().__init__('not scraping youtube link: \'{}\''.format(url))


class ContentTypeNotAllowed(Exception):
    def __init__(self, content_type):
        super().__init__('invalid content type: \'{}\''.format(content_type))


def get_text_for_url_safe(url, tika_rest_url):
    """
    Safe alternative to get_text_for_url, which may raise exceptions.

    Will return the same dict as get_text_for_url, but will have an
    'exception' field is an exception was raised. The 'text' field will
    be null for compatibility reasons in this case.
    :param url: URL to scrape.
    :param tika_rest_url: URL to Tika REST service.
    :return: dict with 'text' and 'exception' field on error, 'text' and
    'content-type' fields on success.
    """
    try:
        return get_text_for_url(url, tika_rest_url)
    except Exception as exception:
        return {
            'text': None,
            'exception': repr(exception)
        }


def get_text_for_url(url, tika_rest_url):
    """
    Extract text from URL. The raw content is passed to Tika for extraction.

    If the URL is a youtube link or has an invalid content type, the value for
    the 'text' key will be None.
    :param url: URL to scrape.
    :param tika_rest_url: URL to Tika REST service.
    :return: dict with 'text' and 'content-type' KV pair.
    """
    _check_url(url)

    headers = requests.head(url).headers
    content_type = headers['content-type']
    _check_content_type(content_type)

    document = requests.get(url).content
    response = requests.post(tika_rest_url, files={'file': document})
    return {
        'text': response.json()['text'],
        'content-type': content_type
    }


def get_download_url(url):
    """
    Returns download URL for given URL. Configured for SURFdrive links only at
    the moment. SURFdrive URLs on SURFsharekit pages point to HTML pages, and
    need '/download' attached at the end of their path.

    If not a SURFdrive URL, will return the URL as is.
    :param url: URL to reformat, if necessary.
    :return: reformatted URL, if reformatting was necessary.
    """
    if 'surfdrive.surf.nl' in url:
        return '{}/download'.format(url)

    return url


def _check_url(url):
    """
    Check that a URL is a valid target for text extraction. At the moment,
    Youtube links are not scraped.
    :param url: URL to check.
    :return: None, throws exception if URL is is invalid.
    """
    if 'youtube.com' in url:
        raise IsYoutubeLink(url)


def _check_content_type(content_type):
    """
    Check for allowed content type. Throws exception if not allowed.
    :param content_type: content type string, as returned by HTTP HEAD.
    :return: None, throws exception if content type not allowed.
    """
    if content_type in ALLOWED_CONTENT_TYPES or 'text/html' in content_type:
        return

    raise ContentTypeNotAllowed(content_type)
