import re
import argparse
from bs4 import BeautifulSoup
from langchain_community.document_loaders import RecursiveUrlLoader

def bs4_extractor(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\n\n+", "\n\n", soup.text).strip()


def get_urls_docs(url):
    loader = RecursiveUrlLoader(
        url,
        extractor=bs4_extractor,
        prevent_outside=True,
        max_depth=7,
        #base_url="https://elasticpath.dev/docs/commerce-manager",
        base_url="https://elasticpath.dev/guides",
        #link_regex=r'<a\s+(?:[^>]*?\s+)?href="([^"]*(?=index)[^"]*)"',
        exclude_dirs=['https://elasticpath.dev/docs/customer-management', 
                    'https://elasticpath.dev/docs/api/customer-addresses',
                    'https://elasticpath.dev/docs/api/promotions',
                    'https://elasticpath.dev/docs/commerce-manager/product-experience-manager',
                    'https://elasticpath.dev/docs/commerce-manager/promotions-standard']
    )

    docs = loader.load()

    #print(f"Page content is {docs[0].page_content}")
    # print all the source attributes
    for doc in docs:
        print(f"Source is {doc.metadata['source']}")

    print(f"Sourcing {len(docs)} web pages")

    return docs 

#documents = get_recursive_docs("https://elasticpath.dev/docs/commerce-manager")
