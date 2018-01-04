import argparse
import os.path
import sys
import urllib.parse

import aiohttp
import async_timeout
import asyncio
from lxml import html


def format_urls(*args):
    return urllib.parse.urljoin(*args)


class Crawler:
    CRAWLED_LINKS = []

    def __init__(self, depth=2, urls=[], *args, **kwargs):
        self._depth = depth
        self._urls = urls
        self._step = 0

        self.CRAWLED_LINKS = []

    def set_depth(self, depth, *args, **kwargs):
        self._depth = depth

    def set_urls(self, urls, *args, **kwargs):
        self._urls = urls

    async def _process(self, url, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                async with session.get(url) as response:
                    if response.status == 200:
                        _html = await response.text()
                        _tree = html.fromstring(_html)
                        _links = _tree.cssselect(
                            'a[href^="/"]:not(a[href^="//"]):not(a[href*="."])'
                        )

                        for link in _links:
                            self.CRAWLED_LINKS[-1].add(
                                format_urls(url, link.get('href'))
                            )

    async def _parse(self, *args, **kwargs):

        if self._step == self._depth:
            return None

        for index in range(self._step, self._depth):

            print(' Depth #{} '.format(index + 1).center(20, '-'))

            urls = []
            if not len(self.CRAWLED_LINKS):
                urls = self._urls
            elif len(self.CRAWLED_LINKS) == 1:
                urls = self.CRAWLED_LINKS[-1].difference(set(self._urls))
            else:
                urls = (
                    self.CRAWLED_LINKS[-1].difference(
                        self.CRAWLED_LINKS[-2])
                )

            self.CRAWLED_LINKS.append(set())

            for url in urls:
                print('Processing: {}'.format(url))
                await self._process(url)

        self._step = self._depth

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback, *args, **kwargs):
        pass

    @property
    def _formatted_data(self):
        return sorted(set(
            link
            for links in self.CRAWLED_LINKS
            for link in links
        ))

    @property
    async def results(self, *args, **kwargs):
        await self._parse()
        return self._formatted_data

    async def save(self, output, *args, **kwargs):
        await self._parse()
        with open(output, 'w') as file:
            links = self._formatted_data
            for link in links:
                file.write(link + '\n')
        return None


if __name__ == "__main__":
    _parser = argparse.ArgumentParser(description='Web Crawler')

    _parser.add_argument(
        '--depth', default=1, type=int,
        help='Configure depth of crawling'
    )

    _parser.add_argument(
        '--output', type=str,
        help='Output file',
        default=os.path.join(os.path.abspath('.'), 'output.txt')
    )

    _parser.add_argument(
        '--input', type=str,
        help='Input file',
        default=os.path.join(os.path.abspath('.'), 'input.txt')
    )

    arguments = _parser.parse_args()

    if not os.path.exists(arguments.input):
        sys.exit('Input file does not exists')

    crawler = Crawler(depth=arguments.depth)

    with open(arguments.input) as file:
        urls = []
        for line in file:
            urls.append(line.strip())

        crawler.set_urls(urls)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.save(arguments.output))
    loop.close()
