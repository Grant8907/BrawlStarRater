import os
import time
import re
import urllib.parse
from typing import Optional

import requests
from bs4 import BeautifulSoup

BASE_WIKI = "https://brawlstars.fandom.com"
CATEGORY_URL = f"{BASE_WIKI}/wiki/Category:Brawlers"
OUTPUT_DIR = "brawler_images_default"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BrawlerDefaultSkinScraper/1.0; +https://example.com)"
}

session = requests.Session()
session.headers.update(HEADERS)


def get_soup(url: str) -> BeautifulSoup:
    resp = session.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def get_brawler_links() -> dict:
    """
    Return dict {name: page_url}.

    Simple approach: take all /wiki/ links on the Category page,
    and skip obvious non-article things like Category:, File:, Special: etc.
    """
    print(f"Fetching category page: {CATEGORY_URL}")
    soup = get_soup(CATEGORY_URL)

    brawlers = {}

    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]

        if not text:
            continue

        # Only wiki article links
        if not href.startswith("/wiki/"):
            continue

        # Skip category, file and special pages
        if href.startswith("/wiki/Category:"):
            continue
        if href.startswith("/wiki/File:"):
            continue
        if href.startswith("/wiki/Special:"):
            continue

        url = urllib.parse.urljoin(BASE_WIKI, href)
        brawlers[text] = url

    print(f"Found {len(brawlers)} candidate pages.")
    return brawlers


def pick_default_skin_image_url(soup: BeautifulSoup, brawler_name: str) -> Optional[str]:
    """
    Try to find a DEFAULT-skin image for this brawler.

    Strategy:
    - Look at all <img> tags and inspect metadata attributes:
      alt, data-image-name, data-image-key
    - If any of those contain 'Skin-Default' (case-insensitive), use that image.
    - If nothing matches, return None.
    """
    target = "skin-default"
    imgs = soup.find_all("img")

    for img in imgs:
        meta_parts = []
        for attr in ("alt", "data-image-name", "data-image-key"):
            val = img.get(attr)
            if val:
                meta_parts.append(str(val))

        combined_meta = " ".join(meta_parts).lower()

        if target in combined_meta:
            src = img.get("data-src") or img.get("src")
            if not src:
                continue

            return urllib.parse.urljoin(BASE_WIKI, src)

    return None


def slugify(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name)
    return name or "unknown"


def download_image(name: str, url: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".png"
    filename = f"{slugify(name)}_default{ext}"
    path = os.path.join(OUTPUT_DIR, filename)

    print(f"  → Downloading {name} default skin: {url} -> {path}")
    resp = session.get(url, stream=True)
    resp.raise_for_status()

    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def main():
    brawlers = get_brawler_links()
    print("Starting default-skin downloads…")

    for name, url in sorted(brawlers.items()):
        print(f"\n{name}: {url}")
        try:
            soup = get_soup(url)
            img_url = pick_default_skin_image_url(soup, name)
            if not img_url:
                print("  !! No default skin image (Skin-Default) found, skipping.")
                continue

            download_image(name, img_url)
            time.sleep(1)  # be kind to the server
        except Exception as e:
            print(f"  !! Error for {name}: {e}")


if __name__ == "__main__":
    main()