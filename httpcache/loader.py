import requests
import time


def default_session():
    return requests.Session()


# Ich schäme mich für diesen Klassennamen.
# Leider sind alle anderen auch nicht klarer, im Moment
class Loader(object):
    '''The loader follows urls and loads their content.'''
    def __init__(self, session=None):
        self._session = session or default_session()

    def follow(self, url):

        # TBD: This method should die,
        # It was forked to web.download
        # and should use this class in the future.
        # Until then, no direct downloads for you.

        # Look out for the following:
        # - The downloader class has not been tried with the throttle.
        # - Earlier versions returned 599 in case the server was unreachable
        #   as of requests.exceptions.ConnectionError
        # - New Downloader also returns Content-Disposition Headers
        raise NotImplemented()


        '''If the request was redirected, the intermediate hops are also
        returned, which is why the follow function yields multiple results.
        '''
