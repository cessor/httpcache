from . import logmessage
from .httpheader import HttpHeader
import logging


class Download(object):
    def __init__(self, session):
        self._session = session

    def _hop(self, intermediate_response):
        hop = intermediate_response
        source = hop.url
        status_code = hop.status_code

        header = HttpHeader(hop.headers)
        content_type = header.content_type
        content_disposition = header.content_disposition
        target = header.location
        return (
            source,
            status_code,
            content_type,
            content_disposition,
            target
        )

    def _hops(self, history):
        '''Returns intermediate redirection hops.
        This is helpful because DOIs are often linked
        with chains of redirects, e.g.

        dx.doi.org/<doi>           (1)
            -> doi.acm.org/<doi>   (2)
                -> dl.acm.org/<id> (3)

        These intermediate responses are returned,
        so that the cache can resolve documents locally.

        This is useful when different pages point to different locations
        in the chain. Imagine Page A and Page B to be publisher pages
        or blogs. If Page A points to dx.doi.org/<doi>, and Page B points to
        doi.acm.org/<doi>, they refer to the same document (dl.acm.org),
        but the cache would attempt a new download, because it thinks
        they are different documents.
        '''
        return (self._hop(response) for response in history)

    def get(self, url):
        '''Returns a response object for each redirection step'''

        content = None
        content_type = None
        content_disposition = None

        try:
            logging.info(logmessage.RETRIEVING + str(url))
            response = self._session.get(url)
            logging.debug(logmessage.RESPONSE + str(response))

        except Exception as exception:
            logging.debug(logmessage.EXCEPTION + str(exception))
            raise

        # Handle Redirects
        if response.history:
            logging.info(logmessage.REDIRECTS + str(url))
            yield from self._hops(response.history)

        # Handle End of Redirect Chain
        header = HttpHeader(response.headers)

        yield (
            response.url,
            response.status_code,
            header.content_type,
            header.content_disposition,
            response.content
        )