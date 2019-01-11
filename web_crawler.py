import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests as requests
from bs4 import BeautifulSoup

# just follow obsolute links per spec
VALID_HREF_REGEX = re.compile("(^http://|https://)")
# probably better as command line argument, but following the spec here
MAX_DEPTH = 3
# throttle async processing
NUM_WORKERS = 6


def extract_child_links(link: str) -> set:
    """Loads page and extracts all unique links within the page."""
    # possible exceptions abound below, caller will handle these
    req = requests.get(link)
    html_page = req.text
    parser = BeautifulSoup(html_page, 'html.parser')
    child_links = parser.findAll('a', attrs={'href': VALID_HREF_REGEX})
    # return unique set child links
    return {link.get('href') for link in child_links}


def dump_links(parent: str, children: set):
    """Prints parent and child links in indented style requested in spec."""
    print(parent)
    [print('  ', c) for c in children]


def crawl(links: set, executor, processed_links: set, level=0):
    """Recursively crawls a set of links up to MAX_DEPTH"""
    if level < MAX_DEPTH:
        # submit each link to thread pool
        future_to_link = {executor.submit(extract_child_links, link): link for link in links}
        # print results as they complete
        for future in as_completed(future_to_link):
            parent = future_to_link[future]
            # track processed links for filtering below
            processed_links.add(parent)
            try:
                # next call will propagate (from thread pool) any link
                # processing errors (e.g. network, bad url, bad html)
                child_links = future.result()
                # our objective
                dump_links(parent, child_links)
                # ensure we don't follow cycles or waste time on known bad links
                to_crawl = child_links - processed_links
                crawl(to_crawl, executor, processed_links, level + 1)
            except Exception as e:
                print('INVALID LINK: {} DETAILS: {}'.format(parent, e))


def main():
    # requested links to crawl
    initial_links = set(sys.argv[1:])
    # for cycle detection. Obviously this in-memory set is an issue if crawler would need to operate at scale
    processed_links = set()
    # use a single thread pool for the entire program. context manager will close it when we are done
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        crawl(initial_links, executor, processed_links)


if __name__ == "__main__":
    main()
