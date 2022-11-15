import urllib3.exceptions
from bs4 import BeautifulSoup, SoupStrainer
import requests
from timeit import timeit
import os
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath


@timeit
def scrape(from_url: str, to_directory_path: str, target_nesting_level: int = 1):
    def _prepare_directory():
        if not os.path.exists(to_directory_path):
            os.mkdir(to_directory_path)
            print(f"Directory {to_directory_path} is created")

    @timeit
    def _scrape_recursive(previous_url, target_url, current_nesting_level):
        parsed_url = urlparse(target_url)
        if parsed_url.netloc != "":
            if parsed_url.netloc != start_netloc:
                return
        else:
            target_url = previous_url + target_url

        if target_url in visited_urls:
            return

        try:
            page = requests.get(target_url)
            if page.status_code == 200:
                path = PurePosixPath(unquote(parsed_url.path))
                directory_parts = list(path.parts[1:])
                if parsed_url.params != "":
                    directory_parts.append(parsed_url.params)
                if parsed_url.query != "":
                    directory_parts.append(parsed_url.query)
                if parsed_url.fragment != "":
                    directory_parts.append(parsed_url.fragment)
                if len(directory_parts) > 0:
                    filename = directory_parts[-1] + ".html"
                else:
                    filename = "index.html"
                directory_path = netloc_directory
                for part in directory_parts:
                    directory_path = os.path.join(directory_path, part)
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                full_path = os.path.join(directory_path, filename)
                with open(full_path, "wb") as file:
                    file.write(page.content)

                if current_nesting_level < target_nesting_level:
                    for link in BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer('a')):
                        if link.has_attr('href'):
                            _scrape_recursive(target_url, link['href'], current_nesting_level + 1)
        except urllib3.exceptions.LocationParseError:
            print(f"Couldn't parse URL {target_url}")
        finally:
            visited_urls.add(target_url)

    _prepare_directory()
    start_netloc = urlparse(from_url).netloc
    netloc_directory = os.path.join(to_directory_path, start_netloc)
    visited_urls = set()

    _scrape_recursive(None, from_url, 1)
