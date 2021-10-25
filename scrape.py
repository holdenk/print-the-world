# 
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from retry import retry


def extract_links(url):
    links = []
    f = requests.get(url)
    soup = BeautifulSoup(f.text, 'html.parser')
    links = soup.find_all('a')
    urls = []
    for l in links:
        try:
            urls.append(l["href"])
        except:
            pass
    return urls


base = "https://3d.si.edu/"

def links_for_page(id):
    """Get all of the links for page X of the smithstonian results."""
    # They live at https://3d.si.edu/explore?page=X
    # grab smithsonian webpage
    return filter(is_3d_model, extract_links(f'https://3d.si.edu/explore?page={id}'))


def is_3d_model(url):
    """Is the link (probably) to a 3D model?"""
    return url.startswith("/object/3d")

@retry(delay=60, tries=5, backoff=2, max_delay=600)
def extract_model_info(url):
    """Find the model information."""
    try:
        return _do_extract_model_info(url)
    except Exception as e:
        print(f"Got exception {e}")
        raise e

def _do_extract_model_info(url):
    print(f"Fetching model {url}")
    info = {}
    info["friendly_url"] = url
    links = []
    f = requests.get(f"{base}{url}")
    soup = BeautifulSoup(f.text, 'html.parser')
    title = soup.title.string
    links = soup.find_all('a')
    id = url.split(":")[-1]
    model_data_url = f"https://ids.si.edu/ids/media_view?id=3d_package%3A{id}&format=json"
    model_data_req = requests.get(model_data_url)
    model_data = json.loads(model_data_req.text)
    dls = model_data["downloads"]
    file_url = None
    description_element = soup.find("div", {"id": "edanDetails"}) or soup.find("div", {"id": "edanWrapper"})
    description_text = description_element.text
    for r in dls:
        # Select the max resolution and 
        if file_url is None or ("Full" in r["label"] and not "combined" in file_url):
            file_url = r["url"]
    return {"title": title, "file_url": file_url, "description": description_text, "friendly_url": f"{base}{url}"}

def can_slice(url):
    """Is there anything at the link we can slice."""


first_page_links = list(filter(is_3d_model, links_for_page(1)))

# Some details: the smithstonian website loops infinitely (e.g. ask for page 100000 and it will always give you some data back).
page = 1
no_repeats = True
c = 0

with open('rejects', 'w') as rejects:
    with open('candidates.csv', 'w') as outfile:
        fieldnames = ['file_url', 'friendly_url', 'title', 'description']
        candidate_writer = csv.DictWriter(outfile, fieldnames = fieldnames, quoting=csv.QUOTE_NONNUMERIC, escapechar='\\')
        candidate_writer.writeheader()
        while no_repeats:
            print(f"Up to candidate {c} on page {page}")
            new_links = list(filter(is_3d_model, links_for_page(page)))
            for link in new_links:
                try:
                    model = extract_model_info(link)
                    candidate_writer.writerow(model)
                except Exception as e:
                    print(f"Had error {e} on {link}")
                    rejects.write(f"{link}\n")
                c = c + 1
            if page != 1:
                for l in new_links:
                    if l in first_page_links:
                        no_repeats = False
            page = page + 1
