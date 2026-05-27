from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


START_URL = "https://en.mpgu.su/homempgu/"

BASE_DOMAIN = "en.mpgu.su"

RAW_DATA_DIR = Path("data/raw")

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


class MPGUCrawler:
    def __init__(self, max_pages=50):
        self.max_pages = max_pages

        self.visited = set()

        self.queue = deque([START_URL])

    def is_valid_url(self, url: str):
        parsed = urlparse(url)

        if parsed.netloc != BASE_DOMAIN:
            return False

        blocked_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".svg",
            ".pdf",
            ".zip",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
        )

        if url.lower().endswith(blocked_extensions):
            return False

        return True

    def clean_text(self, text: str):
        lines = text.splitlines()

        cleaned = []

        for line in lines:
            line = line.strip()

            if len(line) < 2:
                continue

            cleaned.append(line)

        return "\n".join(cleaned)

    def extract_text(self, soup: BeautifulSoup):
        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript",
        ]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        return self.clean_text(text)

    def save_page(self, url: str, text: str):
        parsed = urlparse(url)

        path = parsed.path.strip("/")

        if not path:
            path = "homepage"

        filename = path.replace("/", "_") + ".txt"

        filepath = RAW_DATA_DIR / filename

        filepath.write_text(text, encoding="utf-8")

        print(f"Saved: {filename}")

    def extract_links(self, soup: BeautifulSoup, current_url: str):
        discovered = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"]

            absolute_url = urljoin(current_url, href)

            absolute_url = absolute_url.split("#")[0]

            absolute_url = absolute_url.rstrip("/")

            if self.is_valid_url(absolute_url):
                discovered.append(absolute_url)

        return discovered

    def crawl(self):
        page_count = 0

        while self.queue and page_count < self.max_pages:
            current_url = self.queue.popleft()

            if current_url in self.visited:
                continue

            print(f"\nCrawling: {current_url}")

            self.visited.add(current_url)

            try:
                response = requests.get(
                    current_url,
                    timeout=15,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    }
                )

                if response.status_code != 200:
                    print(f"Failed: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                text = self.extract_text(soup)

                if len(text) > 200:
                    self.save_page(current_url, text)

                links = self.extract_links(
                    soup,
                    current_url
                )

                for link in links:
                    if link not in self.visited:
                        self.queue.append(link)

                print(f"Discovered links: {len(links)}")

                page_count += 1

            except Exception as exc:
                print(f"Error: {exc}")

        print("\nCrawling completed")

        print(f"Pages crawled: {page_count}")

        print(f"Unique URLs visited: {len(self.visited)}")


if __name__ == "__main__":
    crawler = MPGUCrawler(max_pages=50)

    crawler.crawl()