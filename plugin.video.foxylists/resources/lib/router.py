try:
    from urllib import urlencode
    from urlparse import urlparse, parse_qsl
except ImportError:
    from urllib.parse import urlencode, urlparse, parse_qsl
import sys

import xbmcaddon



class Router(object):
    def __init__(self):
        self.paths = {}
        self.addon = xbmcaddon.Addon()
        self.id_ = self.addon.getAddonInfo('id')
        self.handle = int(sys.argv[1])

    def route(self, path):
        if path in self.paths:
            raise ValueError('Route already definted')
        def wrapper(func):
            self.paths[path] = func
            return func
        return wrapper

    def run(self):
        full_path = ''.join(sys.argv[0:3:2])
        parsed = urlparse(full_path)
        path = parsed.path
        kwargs = dict(parse_qsl(parsed.query))
        func = self.paths[path]
        return func(**kwargs)

    def build_url(self, func, **kwargs):
        inverted = {v: k for k, v in self.paths.items()}
        path = inverted[func]
        url = 'plugin://{}/{}'.format(self.id_, path)
        if kwargs:
            query = urlencode(kwargs)
            url += '?' + query
        return url


router = Router()
