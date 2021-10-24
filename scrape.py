# 
import requests
from bs4 import BeautifulSoup
def extract_links(url):
    links = []
    f = requests.get(url)
    # print(links)
    soup = BeautifulSoup(f.text, 'html.parser')
    links = soup.find_all('a')
    urls = []
    for l in links:
        try:
            urls.append(l["href"])
        except:
            pass
    return urls


def links_for_page(id):
    """Get all of the links for page X of the smithstonian results."""
    # They live at https://3d.si.edu/explore?page=X
    # grab smithsonian webpage
    return extract_links(f'https://3d.si.edu/explore?page={id}')


def is_3d_model(url):
    """Is the link (probably) to a 3D model?"""
    

def extract_model_link(url):
    """Find the model to download given a model page."""

def can_slice(url):
    """Is there anything at the link we can slice."""


first_page_links = links_for_page(1)
print(first_page_links)
valid_first_page_links = list(filter(is_3d_model, first_page_links))
# Some details: the smithstonian website loops infinitely (e.g. ask for page 100000 and it will always give you some data back).
page = 2
#while True:
#    page = page + 1
#     new_links = list(filter(is_3d_model, links_for_page(page)))
