from pathlib import Path

import requests
from bs4 import BeautifulSoup

from clean_text import clean_text
from urls import MPGU_URLS


RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


class WebLoader:
    def __init__(self):
        self.urls = MPGU_URLS

    def fetch_page(self, url: str) -> str:
        """Download webpage HTML."""

        print(f"\nFetching: {url}")

        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        return response.text

    def extract_text(self, html: str) -> str:
        """Extract useful text from HTML."""

        soup = BeautifulSoup(html, "lxml")

        # Remove junk tags
        for tag in soup([
            "script",
            "style",
            "noscript",
            "header",
            "footer",
            "svg",
            "img",
            "nav",
        ]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        return clean_text(text)

    def save_text(self, url: str, text: str):
        """Save extracted text locally."""

        filename = (
            url.replace("https://", "")
            .replace("http://", "")
            .replace("/", "_")
            .strip("_")
        )

        file_path = RAW_DATA_DIR / f"{filename}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved: {file_path}")

    def run(self):
        """Run ingestion pipeline."""

        for url in self.urls:
            try:
                html = self.fetch_page(url)
                text = self.extract_text(html)
                self.save_text(url, text)

            except Exception as e:
                print(f"Error processing {url}: {e}")


if __name__ == "__main__":
    loader = WebLoader()
    loader.run()