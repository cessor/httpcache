'''Downloads websites and caches them in a sqlite3 database.
If the page was downloaded before, it retrieves it from the cache.
I used this to retrieve websites that lock you out if you request the same
page too often.

Free software. Use and change. Improve and distribute. Give credit.
Be excellent to each other.
Author, Johannes Feb 2017, http://cessor.de
'''
import datetime
import requests
import sqlite3
import time

from collections import namedtuple

columns = ['url', 'status_code', 'content_type', 'content', 'retrieved_at']
UrlRecord = namedtuple('UrlRecord', columns)


HTML_CACHE = 'cache.sqlite'


def timestamp():
    now = datetime.datetime.now()
    return now.isoformat()


def default_session():
    return requests.Session()


class Throttle(object):
    '''Waits before issuing a request.

    Some sites may lock you out when you issue too many requests too quickly.
    The throttle only applies to web requests. Obviously, getting stuff from
    cache is fast if the file is already cached.
    '''
    def __init__(self, session=None, pause=1):
        self._session = session or default_session()
        self._pause = pause

    def get(self, url):
        time.sleep(self._pause)
        return self._session.get(url)


class Cache(object):
    '''Returns http responses for a url.

        Records
        =======
        The cache returns records containing

            1. status code
            2. content type
            3. timestamp
            4. response content

        If the website has been downloaded before, it returns the copy, if not,
        it downloads the site and returns the result.

        Use it as a context manager in a with statement,
        to prevent forgetting to close the database.

        Custom Sessions
        ===============

        In case you need to authenticate (e.g. get a login cookie first,
        or provide specific headers to the request,
        you can use the session-Parameter of the ctor.

        Pass it a <requests.Session> object (See Requests: HTTP For Humans)
        Or any object with a get function that can download urls.
    '''
    def __init__(self, path='', session=None):
        self.connection = sqlite3.connect(path or HTML_CACHE)
        self._initialize_database()
        self._session = session or default_session()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.connection.commit()
        self.connection.close()

    def _follow(self, url):
        content = None
        content_type = None
        response = self._session.get(url)

        # Handle Redirects
        for hop in response.history:
            source = hop.url
            status_code = hop.status_code
            content_type = hop.headers.get('Content-Type')
            target = hop.headers.get('Location')
            yield source, status_code, content_type, target

        # Handle End of Redirect Chain
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type').strip()
            try:
                # Optimistic Guess of Encoding
                # for xml and html
                content = response.content.decode('utf-8')

                # Ideally:
                # if content_type == 'application/pdf':
            except:
                content = response.content

        yield response.url, response.status_code, content_type, content or ''

    def _execute(self, sql, params):
        return self.connection.cursor().execute(sql, params)

    def _initialize_database(self):
        sql = """create table if not exists cache (
            id integer primary key not null,
            url text not null unique,
            status_code integer not null,
            content_type text,
            content text,
            retrieved_at datetime default current_timestamp
        )"""
        self._execute(sql, ())

        sql = """create index if not exists url_index on cache (url)"""
        self._execute(sql, ())
        self.connection.commit()

    def _insert(self, url, status_code, content_type, content):
        sql = """insert into cache (url, status_code, content_type, content)
            values (?, ?, ?, ?)"""
        self._execute(sql, (url, status_code, content_type, content))
        self.connection.commit()

    def _retrieve(self, url):
        sql = """select url, status_code, content_type, content, retrieved_at
            from cache
            where url = ?
            limit 1"""
        return self._execute(sql, (url,)).fetchone()

    def clear(self):
        sql = """delete from cache"""
        self._execute(sql, ())

    def _is_redirect(self, status_code):
        return 300 <= status_code < 400

    def get(self, url):
        record = self._retrieve(url)
        # Tbd: Check if the record is to old. Download anew if so.

        if not record:
            # Iterate over all hops and save intermediate results
            for url, status_code, content_type, content in self._follow(url):
                try:
                    self._insert(url, status_code, content_type, content)
                except sqlite3.IntegrityError:
                    # When redirecting, in case an intermediate hop is already
                    # in the cache chain, return the intermediate hop instead:
                    return self.get(url)

            # Note: Python loops leak their variables.
            # This therefore returns the last file in a redirect chain
            return UrlRecord(url,
                             status_code,
                             content_type,
                             content,
                             timestamp()
                             )

        # The record is present in the chache
        # Resolve redirect chain until the end is reached
        record = UrlRecord(*record)
        while self._is_redirect(record.status_code):
            record = self.get(record.content)
            record = UrlRecord(*record)
            # TBD: This may run forever
        return record

    def list(self):
        sql = """select url, status_code, content_type, retrieved_at
            from cache"""
        for record in self._execute(sql, ()):
            # CSV String
            print(', '.join(map(str, record)))

    def remove(self, url):
        sql = """delete from cache
            where url = ?"""
        self._execute(sql, (url,)).fetchone()
        self.connection.commit()


__all__ = ['Cache', 'Throttle']


def remove(cache, url):
    cache.remove(url)


def load_url(cache, url):
    record = cache.get(url)
    print(record.content)


def main(args):
    pause = 0
    if '-t' in args:
        pause = 1
        args = [arg for arg in args if arg != '-t']

    with Cache(session=Throttle(pause=pause)) as cache:
        if '-c' in args:
            prompt = 'Clear cache? This deletes all cached urls.\nYes / No> '
            answer = input()
            answer = answer.strip().lower()
            if answer and answer in ['y', 'yes']:
                cache.clear()
                print('Cache cleared.')
            return

        if '-l' in args:
            cache.list()
            return

        elif '-r' in args:
            urls = [url for url in args if not url == '-r']
            action = remove

        else:
            urls = args
            action = load_url

        for url in urls:
            action(cache, url)


def no_arguments():
    return len(sys.argv) < 2


def print_usage():
    import os
    script = os.path.basename(__file__)
    message = """{script}. Downloads and caches websites.

Usage: {script} [-r, -l] <url1> [<url2> <url3> ...]

\t-t:\tThrottle requests to 1 per second
\t-l:\tLists urls in cache
\t-r:\tRemoves urls
\t-c:\tClear cache (removes all data)"""

    message = message.format(script=script)
    print(message)


if __name__ == '__main__':
    import sys
    from urllib.parse import urlparse
    if no_arguments():
        print_usage()
        exit()

    main(sys.argv[1:])
