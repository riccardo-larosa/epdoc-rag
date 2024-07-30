import re
import argparse
from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader

def bs4_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup.text).strip()


def get_recursive_docs(url):
    loader = RecursiveUrlLoader(
        #"https://elasticpath.dev/api",
        #"https://elasticpath.dev/docs/commerce-manager/product-experience-manager/Products/overview",
        url,
        extractor=bs4_extractor,
        prevent_outside=True,
        max_depth=7,
        #base_url="https://elasticpath.dev/docs/api/",
        base_url="https://elasticpath.dev/docs/commerce-manager",
        #link_regex=r'<a\s+(?:[^>]*?\s+)?href="([^"]*(?=index)[^"]*)"',
        exclude_dirs=['https://elasticpath.dev/docs/customer-management', 
                    'https://elasticpath.dev/docs/api/customer-addresses',
                    'https://elasticpath.dev/docs/api/promotions/']
    )

    docs = loader.load()

    #print(f"Page content is {docs[0].page_content}")
    # print all the source attributes
    for doc in docs:
        print(f"Source is {doc.metadata['source']}")

    print(f"Loaded {len(docs)} documents")

    return docs 

parser = argparse.ArgumentParser()
parser.add_argument('url', type=str, help='The URL to process')
args = parser.parse_args()

if args.url.startswith("url="):
    url = args.url.split('=', 1)[1]
    print(f"🌐 Loading Documents from Webpage: {url}")
    documents = get_recursive_docs(url)

