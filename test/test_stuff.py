from nose.tools import *

from ..slug import Slug


def test_domain_to_directory():
    expected = 'www-disi-unige-it'
    url = 'www.disi.unige.it'
    actual = Slug('')._domain_to_directory(url)
    assert_equal(actual, expected)


def test_path_to_directory():
    expected = 'person-CazzolaW-RAM-SE04_Proceedings'
    path = '/person/CazzolaW/RAM-SE04 Proceedings/'
    path = Slug('')._path_to_directory(path)
    assert_equal(path, expected)


def test_make_path_from_url():
    expected = 'www-disi-unige-it\person-CazzolaW-RAM-SE04_Proceedings\Gibbs and Coady.pdf'
    url = 'http://www.disi.unige.it/person/CazzolaW/RAM-SE04%20Proceedings/Gibbs%20and%20Coady.pdf'
    path = str(Slug(url))
    assert_equal(path, expected)


def test_make_path_from_url_should_work_for_pathless_files():
    url = 'http://www.disi.unige.it/test.pdf'
    path = str(Slug(url))
    expected = r'www-disi-unige-it\test.pdf'
    assert_equal(path, expected)
