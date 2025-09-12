import os
import re
from typing import Iterable

import requests
from bs4 import BeautifulSoup
import pdfkit


def safe_filename(url: str) -> str:
    """Return a filesystem-friendly version of *url*."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", url)


def download_file(url: str, output_dir: str) -> str:
    """Download *url* into *output_dir* and return local path."""
    response = requests.get(url)
    response.raise_for_status()
    filename = os.path.join(output_dir, os.path.basename(url))
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def save_page_as_pdf(url: str, output_dir: str) -> str:
    """Save the page at *url* as a PDF in *output_dir*."""
    filename = os.path.join(output_dir, safe_filename(url) + ".pdf")
    pdfkit.from_url(url, filename)
    return filename


def crawl(urls: Iterable[str], output_dir: str) -> None:
    """Download resources linked from *urls*.

    *urls* may contain HTML pages. Links ending with ``.pdf`` are downloaded
    directly while HTML links are rendered to PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    for url in urls:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            link = requests.compat.urljoin(url, a["href"])
            try:
                if link.lower().endswith(".pdf"):
                    download_file(link, output_dir)
                else:
                    save_page_as_pdf(link, output_dir)
            except Exception as exc:  # pragma: no cover - logging placeholder
                print(f"Failed to fetch {link}: {exc}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m icrawler.crawler <output_dir> <url1> [<url2> ...]")
    else:
        output_dir = sys.argv[1]
        urls = sys.argv[2:]
        crawl(urls, output_dir)
