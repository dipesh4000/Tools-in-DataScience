import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

BASE = "https://sanand0.github.io/tdsdata/crawl_html/"

visited = set()
count = 0

def crawl(url):
    global count

    if url in visited:
        return

    visited.add(url)

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return
    except:
        return

    soup = BeautifulSoup(r.text, "html.parser")

    # count current html file
    path = urlparse(url).path
    filename = path.split("/")[-1]

    if filename.endswith(".html"):
        first = filename[0].upper()
        if "A" <= first <= "U":
            count += 1

    # crawl all html links
    for a in soup.find_all("a", href=True):
        href = a["href"]

        full = urljoin(url, href)

        if full.startswith(BASE) and full.endswith(".html"):
            crawl(full)

crawl(BASE)

print("Count =", count)
print("Visited =", len(visited))



# ques: SiteScout collects competitor pages for market research. Its crawler stores HTML files in alphabetized folders. Estimate workload by counting how many files fall between letters A and U.

# Crawl https://sanand0.github.io/tdsdata/crawl_html/. How many HTML files begin with letters from A to U?

# Number of files


# ans: 94