'''Downloads websites and caches them in a sqlite3 database.
If the page was downloaded before, it retrieves it from the cache.
I used this to retrieve websites that lock you out if you request the same
page too often.

Free software. Use and change. Improve and distribute. Give credit.
Be excellent to each other.
Author, Johannes Feb 2017, http://cessor.de

Todo: I need a better name for this.
'''
from cache import Cache
from loader import Loader, Throttle
from store import Store
from folder import Folder

__all__ = ['Cache', 'Throttle', 'Loader', 'Store', 'Folder']


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

    with Cache(
        store=Store(),
        loader=Loader(
            session=Throttle(
                pause=pause
            )
        ),
        folder=Folder()
    ) as cache:
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

Usage: {script} [-l | -r | -c | -t] <url1> [<url2> <url3> ...]

\t-t:\tThrottle requests to 1 per second

\t-l:\tLists urls in cache as
\t   \t<url>, <status_code>, <Content-Type>, <timestamp>

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
