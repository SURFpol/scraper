# Scraping
This repository contains code for scraping a SURFsharekit repository.

## Installation
[Install conda](https://conda.io/docs/user-guide/install/index.html) 
first, and install the dependencies in a Python 3.6 environment:

**Conda**:
```
> conda install --file requirements.txt
```

An [analyzer](https://github.com/SURFpol/analyzer) REST endpoint is required 
for performing text extraction.

## Scraping a SURFsharekit repository
To scrape a SURFsharekit repository, export the SURFsharekit metadata to 
an `.xlsx` file. Then call the `scrape-surfsharekit.py` script as follows:

```
> scrape-surfsharekit.py [--overwrite] XLSX_FILE OUTPUT_DIRECTORY ANALYZER_REST_URL
``` 

The script will write a JSON file to the output directory for each SURFsharekit 
URL in the `.xlsx` file. The filename for each file will be formatted as 
`<SURFsharekit ID>.json`. `--overwrite` will overwrite a JSON output file, even 
if it exists.

### JSON file format
The format for each JSON file as follows:

```json
{
    "keywords": [
        "geography",
        "earth sciences"
    ],
    "documents": [
        {
            "url": "https://www.youtube.com/watch?v=xxxxxxxxx",
            "title": "Video title",
            "text": null,
            "exception": "IsYoutubeLink(\"not scraping youtube link: 'https://www.youtube.com/watch?v=xxxxxxxxx'\",)"
        },
        {
            "url": "https://surfdrive.surf.nl/files/index.php/s/xxxxxxxxx",
            "title": "Additional material",
            "text": "document text",
            "content-type": "text/html; charset=UTF-8"
        }
    ],
    "url": "https://surfsharekit.nl/publiek/ooo/xxxxxxxxx",
    "id": "xxxxxxxxxxxx"
}
```

Keywords are extracted from the SURFsharekit page, as well as the attachments. 
Each attachment is scraped for its text content. If an error occurred during 
processing, such as when the attachment is a Youtube video or has an invalid 
content type, the `text` field will be null, and the `exception` field will 
contain a dump of the Python exception.
