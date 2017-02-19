import requests
import time


def default_session():
    return requests.Session()


class Throttle(object):
    '''A session that waits before issuing a request.

    Some sites may lock you out when you issue too many requests too quickly.
    The throttle only applies to web requests. Obviously, getting stuff from
    cache is fast when the file is already cached.
    '''

    def __init__(self, session=None, pause=1):
        '''
        Parameters
        ----------

        session: Place a requests.Sessions object here
        pause: Time to wait in seconds
        '''
        self._session = session or default_session()
        self._pause = pause

    def get(self, url):
        time.sleep(self._pause)
        return self._session.get(url)


# Ich schäme mich für diesen Klassennamen.
# Leider sind alle anderen auch nicht klarer, im Moment
class Loader(object):
    '''The loader follows urls and loads their content.'''
    def __init__(self, session=None):
        self._session = session or default_session()

    def follow(self, url):
        '''If the request was redirected, the intermediate hops are also
        returned, which is why the follow function yields multiple results.
        '''
        content = None
        content_type = None
        try:
            response = self._session.get(url)
        except requests.exceptions.ConnectionError:
            # 599 Indicates Network Timeout,
            # according to wikipedia: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#5xx_Server_Error
            return url, 599, None, ''

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
