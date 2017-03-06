from nose.tools import *

from kazookid import Substitute

from httpcache.download import *


def test_download():
    assert_true(Download(None))


def test_download_url():
    # Arrange
    headers = {
        'Content-Type': 'plain/text'
    }

    response = Substitute()
    response.headers = headers
    response.url = 'http://localhost:8888'
    response.status_code = 200
    response.content = "Hello, World"
    response.history = []

    session = Substitute()
    session.get.returns(response)

    # System under Test
    download = Download(session)

    # Act
    record = download.get('http://localhost:8888')

    # Assert
    record = list(record)[0]

    assert_equal(record[0], 'http://localhost:8888')
    assert_equal(record[0], 'http://localhost:8888')
    assert_equal(record[0], 'http://localhost:8888')
    assert_equal(record[0], 'http://localhost:8888')