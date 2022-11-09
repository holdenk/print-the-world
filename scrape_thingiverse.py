# 
import sys
import re
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from retry import retry
from thingiverse import Thingiverse


def extract_links(url):
    links = []
    f = requests.get(url)
    soup = BeautifulSoup(f.text, 'html.parser')
    print(f"Got text {f.text}")
    links = soup.find_all('a')
    print(f"Got links {links}")
    urls = []
    for l in links:
        try:
            urls.append(l["href"])
        except:
            pass
    print(f"Urls {urls}")
    return urls


@retry(delay=60, tries=5, backoff=2, max_delay=600)
def extract_model_info(url, thing_id):
    """Find the model information."""
    try:
        return _do_extract_model_info(url, thing_id)
    except Exception as e:
        print(f"Got exception {e}")
        raise e

def _do_extract_model_info(url, thing_id):
    print(f"Fetching model {url}")
    info = {}
    info["friendly_url"] = url
    links = []
    f = requests.get(url)
    print(f"Got {f} - {f.text}")
    soup = BeautifulSoup(f.text, 'html.parser')
    title = soup.title.string
    links = soup.find_all('a')
    description_element = soup.find("meta", {"property": "og:description"})
    description_text = description_element.attrs['content']
    file_url = f"https://cdn.thingiverse.com/tv-zip/{thing_id}"
    return {"title": title, "file_url": file_url, "description": description_text, "friendly_url": f"{url}"}

def can_slice(url):
    """Is there anything at the link we can slice."""


# Add a header if nothing present
try:
    with open('thing_candidates.csv', 'r') as infile:
        pass
except Exception:
    with open('thing_candidates.csv', 'a') as outfile:
        fieldnames = ['file_url', 'friendly_url', 'title', 'description']
        candidate_writer = csv.DictWriter(outfile, fieldnames = fieldnames, quoting=csv.QUOTE_NONNUMERIC, escapechar='\\')
        candidate_writer.writeheader()

c = 0
key = None
with open('.config', 'r') as keyfile:
    key = keyfile.read()
with open('thing_rejects', 'a') as rejects:
    with open('thing_candidates.csv', 'a') as outfile:
        fieldnames = ['file_url', 'friendly_url', 'title', 'description']
        candidate_writer = csv.DictWriter(outfile, fieldnames = fieldnames, quoting=csv.QUOTE_NONNUMERIC, escapechar='\\')
        c = c + 1
        print(f"Up to candidate {c}")
        with open("tpage", "w") as tpage:
            tpage.write(f"{tpage}")
        results = Thingiverse(access_token=key).search_term("sort=popular").hits
        for result in results:
            link = result.public_url
            thing_id = result.id
            name = result.name
            try:
                model = extract_model_info(link, thing_id)
                print(f"Got {model}")
                candidate_writer.writerow(model)
            except Exception as e:
                print(f"Had error {e} on {link}")
                rejects.write(f"{link}\n")
            c = c + 1
        raise exception("Farts")
