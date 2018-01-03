import argparse
import os.path
import re
import sys
import urllib.parse

import aiohttp
import async_timeout
import asyncio

CRAWLED_LINKS = []


def format_urls(*args):
    return urllib.parse.urljoin(*args)


async def get_links(url):
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    html = html.replace("'", '"')
                    pattern = re.compile(r'a href=\"\/(.+?)\"')
                    for link in re.finditer(pattern, html):
                        _link = link.groups()[0]
                        if (
                            not _link.startswith('/') and
                            _link.endswith('/') and
                            _link != '/'
                        ):
                            CRAWLED_LINKS[-1].add(
                                format_urls(url, '/' + _link))


async def crawl(input_file='', depth=1):
    for _ in range(depth):
        urls = []
        if not len(CRAWLED_LINKS):
            with open(input_file) as file:
                for line in file:
                    urls.append(line.strip())
        else:
            urls = CRAWLED_LINKS[-1]

        CRAWLED_LINKS.append(set())

        for url in urls:
            print('Processing: {}'.format(url))
            await get_links(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web Crawler')

    parser.add_argument(
        '--depth', default=1, type=int,
        help='Configure depth of crawling'
    )

    parser.add_argument(
        '--output', type=str,
        help='Output file',
        default=os.path.join(os.path.abspath('.'), 'crawling.txt')
    )

    parser.add_argument(
        '--input', type=str,
        help='Input file',
        default=os.path.join(os.path.abspath('.'), 'input.txt')
    )

    arguments = parser.parse_args()

    if not os.path.exists(arguments.input):
        sys.exit('Input file does not exists')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl(arguments.input, arguments.depth))
    loop.close()

    with open(arguments.output, 'w') as file:
        for links in CRAWLED_LINKS:
            _links = sorted(links)
            for link in _links:
                file.write(link + '\n')
