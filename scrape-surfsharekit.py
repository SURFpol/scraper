#!/usr/bin/env python
import os
import click

from sharekit import write_sharekit_page_to_json, parse_surfsharekit_excel


@click.command()
@click.argument('input-file')
@click.argument('output-directory')
@click.argument('tika-rest-url')
@click.option('--overwrite', is_flag=True)
def main(input_file, output_directory, tika_rest_url, overwrite):
    sharekit_pages = parse_surfsharekit_excel(input_file)
    click.echo('Found {} SURFsharekit pages in file'.format(len(sharekit_pages)))

    for _id, url in sharekit_pages:
        output_path = os.path.join(output_directory, '{}.json'.format(_id))
        if os.path.exists(output_path) and not overwrite:
            click.echo('Output file for ID {} already exists: {}. Skipping...'.format(
                _id, output_path
            ))
            continue

        click.echo('Writing ID {} to {}'.format(_id, output_path))

        try:
            write_sharekit_page_to_json(url, tika_rest_url, output_path)
        except Exception as exception:
            click.echo('Encountered exception for URL {} (ID: {}): {}'.format(
                url,
                _id,
                repr(exception)
            ))
            break

    click.echo('Done')


if __name__ == '__main__':
    main()
