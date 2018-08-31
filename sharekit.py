import re
from urllib.parse import urlparse
import requests
import json

from toolz import merge
from bs4 import BeautifulSoup
from openpyxl import load_workbook

from scrape import get_text_for_url_safe


_ROW_HYPERLINK_REGEX = re.compile('=HYPERLINK\("(?P<url>[^"]+)","(?P<id>[^"]+)"\)')


def write_sharekit_page_to_json(url, tika_rest_url, output):
    """
    All-in-one function for parsing a SURFsharekit page, extracting its
    keywords and attachments, and scraping the attachment text. Writes out
    a JSON document to the specified output.
    :param url: URL to SURFsharekit page.
    :param tika_rest_url: URL to Tika REST service.
    :param output: path to output file.
    :return: dict that was written to output.
    """
    # Parse keywords and attachments from SURFsharekit page

    page = _parse_surfsharekit_page(requests.get(url).content)

    # Append ID and URL

    page['url'] = url
    page['id'] = _get_id_from_url(url)

    # Extract text for each attachment

    page['documents'] = [
        merge(
            document,
            get_text_for_url_safe(document['url'], tika_rest_url)
        )
        for document in page['documents']
    ]

    # Write out

    with open(output, 'wt') as stream:
        json.dump(page, stream, indent=4)

    return page


def parse_surfsharekit_excel(xlsx_file):
    """
    Parse a list of (URL, ID) tuples from an .xlsx file, as exported by
    SURFsharekit.
    :param xlsx_file: path to Excel file. Must be in .xlsx format!
    :return: list of (URL and ID tuples) for each SURFsharekit page.
    """
    wb = load_workbook(xlsx_file)
    sheet = wb.worksheets[0]
    rows = sheet.rows
    next(rows)  # skip header

    return [_parse_surfshare_kit_link(row) for row in rows]


def _parse_surfshare_kit_link(row):
    """
    Parse the ID and URL from a row in a SURFsharekit export file.
    :param row: openpyxl row.
    :return: (ID, URL) tuple.
    """
    match = _ROW_HYPERLINK_REGEX.match(row[1].value)
    return match.group('id'), match.group('url')


def _get_id_from_url(url):
    """
    Parse SURFsharekit ID from URL.

    :param url: SURFsharekit URL.
    :return: ID for SURFsharekit item.
    """
    return urlparse(url).path.split('/')[-1]


def _parse_surfsharekit_page(html_doc):
    """
    Return keywords, attachment URLs and titles for a SURFsharekit HTML
    document.
    :param html_doc: HTML document as a string.
    :return: dict with keywords list and documents list (url and title).
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    container = soup.find('div', {'class': 'container-fluid'})
    rows = container.find_all('div', {'class': 'row'})
    rows = {_get_row_name(row): row for row in rows}

    try:
        keywords = _get_keywords(_get_content_column(rows['Trefwoorden']))
    except KeyError:
        keywords = []

    return {
        'keywords': keywords,
        'documents': _get_attachments(_get_content_column(rows['Bijlagen']))
    }


def _get_row_name(row_element):
    """
    Get name of row element in document (taken from first column of element).
    :param row_element: row element,
    :return: name of row.
    """
    name_column = row_element.find('div', {'class': 'col-md-3'})
    paragraph = name_column.find('p')
    return paragraph.text


def _get_content_column(row_element):
    """
    Return content column from row in document, the content column being the
    second column in the row.
    :param row_element: row element.
    :return: content element.
    """
    return row_element.find('div', {'class': 'col-md-9'})


def _get_keywords(content_col):
    """
    Parse keywords from keywords content column.

    Keywords are taken from the paragraph tags in the element.
    :param content_col: content column, as returned by get_content_column.
    :return: list of keywords.
    """
    return [p.text for p in content_col.find_all('p')]


def _get_attachments(content_col):
    """
    Return attachment URLs and titles from attachment content column.

    URLs and titles are taken from the a-elements in the element.
    :param content_col: content column of attachment row, as returned by
    get_content_column.
    :return: list of dicts, each containing a 'url' and 'title' KV pair.
    """
    return [
        {
            'url': element['href'],
            'title': element.text
        }
        for element in content_col.find_all('a', href=True)
    ]
