class HttpHeader(object):
    CONTENT_TYPE = 'Content-Type'
    LOCATION = 'Location'
    CONTENT_DISPOSITION = 'Content-Disposition'

    def __init__(self, headers):
        self._headers = headers

    @property
    def content_type(self):
        return self._headers.get(self.CONTENT_TYPE)

    @property
    def location(self):
        return self._headers.get(self.LOCATION)

    @property
    def content_disposition(self):
        return self._headers.get(self.CONTENT_DISPOSITION)