# 
import requests
from bs4 import BeautifulSoup
def extract_links(url):
    
    links = []
    f = requests.get(url)
    links += [url, f.text]
    # print(links)
    soup = BeautifulSoup(f.text, 'html.parser')
    # ssl error for me when looking at smithsonian webpage

    print(soup.prettify())

# grab smithsonian webpage
extract_links('https://3d.si.edu/explore')


    """Get all of the links for page X of the smithstonian results."""
    # They live at https://3d.si.edu/explore?page=X

def is_3d_model(url):
    """Is the link (probably) to a 3D model?"""
    

def extract_model_link(url):
    """Find the model to download given a model page."""

def can_slice(url):
    """Is there anything at the link we can slice."""


first_page_links = extract_links(1)
valid_first_page_links = list(filter(is_3d_model, first_page_links))
# Some details: the smithstonian website loops infinitely (e.g. ask for page 100000 and it will always give you some data back).
while True:
    # Break 

