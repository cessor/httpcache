import datetime
from collections import namedtuple

from assistant.slug import Slug
from store import RecordExists


columns = ['url', 'status_code', 'content_type', 'content', 'retrieved_at']
UrlRecord = namedtuple('UrlRecord', columns)


def timestamp():
    now = datetime.datetime.now()
    return now.isoformat()


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

    def __init__(self, store, loader, folder):
        self._store = store
        self._loader = loader
        self._folder = folder

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._store.close()

    def _is_redirect(self, status_code):
        return 300 <= status_code < 400

    def get(self, url):
        # TBD:
        # This needs to be separated into a store
        # The store handles files and so on

        record = self._store.retrieve(url)
        # Tbd: Check if the record is to old. Download anew if so.

        if not record:
            # Iterate over all hops and save intermediate results
            for record in self._loader.follow(url):

                url, status_code, content_type, content = record
                try:
                    # Store all data in the db, except for pdfs
                    # - Store those in the file system, and
                    # Cache an fs url for them

                    if content_type == 'application/pdf':
                        # Get a clean file name from the url
                        path = str(Slug(url))

                        # Usually, I would avoid this. But here,
                        # We're dealing with side effects anyway. Meh.
                        path = self._folder.store(path, content)

                        # Override the content, so that the db entry points to
                        # the appropriate file
                        content = str(path)

                    self._store.add(url, status_code, content_type, content)

                except RecordExists:
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

    def clear(self):
        self._store.clear()

    def remove(self, url):
        self._store.remove(url)

    def list(self):
        return self._store.list()
