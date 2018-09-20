#!/usr/bin/env python
import os
import requests
import click

from figshare import FigshareArticle, FIGSHARE_DOCUMENT_URL
from scrape import dump_json


@click.command()
@click.argument('figshare-url')
@click.argument('output-directory')
@click.argument('tika-rest-url')
def main(figshare_url, output_directory, tika_rest_url):
    num_written = 0
    for index, document in enumerate(requests.get(figshare_url).json()):
        _id = document['data']['id']
        document_url = '{}/{}'.format(FIGSHARE_DOCUMENT_URL, _id)

        try:
            output_path = os.path.join(output_directory, '{}.json'.format(_id))
            page = FigshareArticle.from_url(document_url, tika_rest_url)
            click.echo('Writing page with ID {} to {}'.format(page.id, output_path))
            dump_json(page.to_dict(), output_path)
            num_written += 1
        except Exception as e:
            click.echo('Skipping document with ID {}: {}'.format(_id, repr(e)))
            continue

    click.echo('Written {} out of {} documents'.format(num_written, index))
    click.echo('Done')


if __name__ == '__main__':
    main()
