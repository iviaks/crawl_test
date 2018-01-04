import argparse
import json
import os
import sys

import asyncio
import motor.motor_asyncio


class MongoDB:
    def __init__(self, *args, **kwargs):
        client = motor.motor_asyncio.AsyncIOMotorClient(
            os.environ.get('MONGO_HOST', 'localhost'),
            27017
        )
        self.db = client[kwargs.get('database', 'test_database')]
        self.collection = self.db[kwargs.get('collection', 'urls')]

    async def _insert(self, document):
        result = await self.collection.insert_one(document)
        print(result.inserted_id)

    def save(self, data={}, *args, **kwargs):
        loop = asyncio.get_event_loop()

        if isinstance(data, list):
            tasks = [self._insert(document) for document in data]
        else:
            tasks = [self._insert(data)]

        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(description='Saving to MongoDB')

    _parser.add_argument(
        '--database', type=str,
        help='Database name',
        default='testing'
    )

    _parser.add_argument(
        '--collection', type=str,
        help='Collection name',
        default='urls'
    )

    _parser.add_argument(
        '--input', type=str,
        help='Input file',
        default=os.path.join(os.path.abspath('.'), 'input.json')
    )

    arguments = _parser.parse_args()

    if not os.path.exists(arguments.input):
        sys.exit('Input file does not exists')

    mongo = MongoDB(
        database=arguments.database,
        collection=arguments.collection
    )

    with open(arguments.input) as file:
        mongo.save(json.load(file))
