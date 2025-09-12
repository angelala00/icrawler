import os
import random
import re
import time
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


def crawl(
    urls: Iterable[str],
    output_dir: str,
    delay: float = 0.0,
    jitter: float = 0.0,
) -> None:
    """Download resources linked from *urls*.

    *urls* may contain HTML pages. Links ending with ``.pdf`` are downloaded
    directly while HTML links are rendered to PDF.

    :param delay: Minimum delay in seconds between requests.
    :param jitter: Additional random delay in seconds added to ``delay``.
    """

    def _sleep() -> None:
        if delay > 0 or jitter > 0:
            time.sleep(delay + random.uniform(0, jitter))

    os.makedirs(output_dir, exist_ok=True)
    for url in urls:
        _sleep()
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            link = requests.compat.urljoin(url, a["href"])
            _sleep()
            try:
                if link.lower().endswith(".pdf"):
                    download_file(link, output_dir)
                else:
                    save_page_as_pdf(link, output_dir)
            except Exception as exc:  # pragma: no cover - logging placeholder
                print(f"Failed to fetch {link}: {exc}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple PDF crawler")
    parser.add_argument("output_dir")
    parser.add_argument("urls", nargs="+")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="minimum delay in seconds between requests",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=0.0,
        help="additional random delay in seconds",
    )
    args = parser.parse_args()

    crawl(args.urls, args.output_dir, delay=args.delay, jitter=args.jitter)
