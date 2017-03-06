# Thank you for helping me out, Jonathan
# http://jtushman.github.io/blog/2013/06/17/sharing-code-across-applications-with-python/
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Httpcache',
    'author': 'Johannes Hofmeister',
    'url': 'https://github.com/cessor/httpcache',
    'download_url': 'https://github.com/cessor/httpcache',
    'author_email': '',
    'version': '1.0',
    'install_requires': ['requests', 'fire'],
    'tests_require': ['nose', 'kazookid'],
    'packages': ['httpcache'],
    'scripts': [],
    'name': 'httpcache'
}

setup(**config)