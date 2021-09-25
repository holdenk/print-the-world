# 
def extract_links(X):
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
