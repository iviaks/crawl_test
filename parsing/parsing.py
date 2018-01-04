import argparse
import json
import os.path
import sys
import urllib.parse

import aiohttp
import async_timeout
import asyncio
from lxml import html


def format_urls(*args):
    return urllib.parse.urljoin(*args)


class Parser:
    _urls = None
    _locked = {}
    data = []

    def __init__(self, urls=None, *args, **kwargs):
        self._urls = urls

    def set_urls(self, urls=[], *args, **kwargs):
        self._urls = urls

    def get_tree(self, _html):
        return html.fromstring(_html)

    def get_keywords(self, tree=None):
        _tag = tree.cssselect('meta[name="keywords"]')
        _keywords = []

        if len(_tag):
            _keywords += [
                keyword.strip()
                for keyword in _tag[0].get('content').split(',')
            ]

        return _keywords

    def get_headers(self, tree=None):
        _tag = tree.cssselect('h1, h2, h3, h4, h5, h6')
        _headers = {}

        if len(_tag):
            for header in _tag:
                if not _headers.get(header.tag):
                    _headers[header.tag] = []
                text = " ".join(
                    item.strip() for item in header.text_content().split('\n'))
                if text is not None and text.strip():
                    _headers[header.tag].append(text.strip())

        return _headers

    def get_title(self, tree=None):
        _tag = tree.cssselect('title')

        if len(_tag):
            title = _tag[0].text_content().strip()

        return title if len(_tag) else None

    def get_images(self, tree=None, url=None):
        images = tree.cssselect('img')

        _images = []

        if len(images):
            for image in images:
                src = image.get('src')
                if src.startswith('/'):
                    src = format_urls(url, src)
                _images.append(src)

        return _images

    def get_links(self, tree=None):
        links = tree.cssselect('a[href^="http"], a[href^="//"]')

        _links = []

        if len(links):
            for link in links:
                href = link.get('href')
                if href.startswith('//'):
                    href = format_urls('http:', href)
                _links.append(href)

        return _links

    async def _parsing(self, url):

        if self._locked.get(url):
            return None

        async with aiohttp.ClientSession() as session:
            print('Processing: {}'.format(url))
            with async_timeout.timeout(50):
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        tree = self.get_tree(html)

                        self._locked[url] = True

                        self.data.append({
                            'url': url,
                            'keywords': self.get_keywords(tree),
                            'headers': self.get_headers(tree),
                            'title': self.get_title(tree),
                            'images': self.get_images(tree, url),
                            'links': self.get_links(tree),
                        })

    @property
    async def results(self, *args, **kwargs):
        tasks = [self._parsing(url) for url in self._urls]
        await asyncio.wait(tasks)
        return self.data

    async def save(self, output=None, *args, **kwargs):
        tasks = [self._parsing(url) for url in self._urls]
        await asyncio.wait(tasks)

        with open(output, 'w') as file:
            json.dump(self.data, file, indent=2)


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(description='URL parser')

    _parser.add_argument(
        '--output', type=str,
        help='Output file',
        default=os.path.join(os.path.abspath('.'), 'output.json')
    )

    _parser.add_argument(
        '--input', type=str,
        help='Input file',
        default=os.path.join(os.path.abspath('.'), 'input.txt')
    )

    arguments = _parser.parse_args()

    if not os.path.exists(arguments.input):
        sys.exit('Input file does not exists')

    with open(arguments.input) as file:
        urls = []
        for line in file:
            urls.append(line.strip())

    parser = Parser(urls)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(parser.save(arguments.output))
    loop.close()
