'''Downloads websites and caches them in a sqlite3 database.
If the page was downloaded before, it retrieves it from the cache.
I used this to retrieve websites that lock you out if you request the same
page too often.

Free software. Use and change. Improve and distribute. Give credit.
Be excellent to each other.
Author, Johannes Feb 2017, http://cessor.de

Todo: I need a better name for this.
'''
from httpcache.cache import Cache
from httpcache.store import Store
from httpcache.download import Download
from httpcache.folder import Folder

import fire
import requests


@fire.Fire
class HttpCache(object):
    '''Downloads and caches websites.'''
    def __init__(self):
        self.cache = Cache(
            store=Store(),
            session=Download(requests.Session()),
            folder=Folder()
        )

    def clear(self):
        '''Clear cache (removes all data)'''
        with self.cache as cache:
            prompt = 'Clear cache? This deletes all cached urls.\nYes / No> '
            answer = input(prompt)
            answer = answer.strip().lower()
            if answer and answer in ['y', 'yes']:
                cache.clear()
                print('Cache cleared.')
            return

    def get(self, *urls):
        with self.cache as cache:
            for url in urls:
                record = cache.get(url)
                print(record.content)

    def list(self):
        '''Lists urls in cache as
<url>, <status_code>, <Content-Type>, <timestamp>'''
        with self.cache as cache:
            cache.list()

    def remove(self, *urls):
        '''Removes urls'''
        with self.cache as cache:
            for url in urls:
                cache.remove(url)