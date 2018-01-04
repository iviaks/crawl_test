import argparse
import os.path
import sys

import asyncio
from crawling.crawling import Crawler
from parsing.parsing import Parser
from saving.saving import MongoDB


async def main(depth, urls, loop):

    print('Starting crawling')
    crawler = Crawler(depth=depth, urls=urls)
    crawled_sites = await loop.create_task(crawler.results)
    print('Crawling successful')
    print()

    print('Starting parsing')
    parser = Parser(crawled_sites)
    parsed_data = await loop.create_task(parser.results)
    print('Parsing successful')
    print()

    print('Starting Saving')
    database = MongoDB(database='testing', collection='urls')
    await loop.create_task(database.save(parsed_data))
    print('Saving successful')


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(description='Web Crawler')

    _parser.add_argument(
        '--depth', default=1, type=int,
        help='Configure depth of crawling'
    )

    _parser.add_argument(
        '--input', type=str,
        help='Input file with urls',
        default=os.path.join(os.path.abspath('.'), 'input.txt')
    )

    arguments = _parser.parse_args()

    if not os.path.exists(arguments.input):
        sys.exit('Input file does not exists')

    urls = []
    with open(arguments.input) as file:
        for line in file:
            urls.append(line.strip())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(arguments.depth, urls, loop))
    try:
        loop.close()
    except RuntimeError:
        pass
