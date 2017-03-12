
import os
from gzip import GzipFile
from io import BytesIO

from flask import request
from werkzeug.contrib.cache import FileSystemCache


def gzip_middleware(app):
    """Strictly speaking, this is not a middleware, but a trigger after the
     response is going to be finished.
    """

    def do_compress(data):
        gzip_buffer = BytesIO()
        with GzipFile(mode='wb',
                      compresslevel=6,
                      fileobj=gzip_buffer) as gzip_file:
            gzip_file.write(data)
        return gzip_buffer.getvalue()

    def compress(response):
        accept_encoding = request.headers.get('Accept-Encoding', '')
        do_encoding = request.args.get('encoding')

        if (not do_encoding
           or 'gzip' not in accept_encoding.lower()
           or not 200 <= response.status_code < 300
           or 'Content-Encoding' in response.headers):

            return response

        gzip_content = do_compress(response.get_data())
        response.set_data(gzip_content)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = response.content_length
        response.direct_passthrough = False

        return response

    app.after_request(compress)

    return app


class CacheMiddleware:
    def __init__(self, app, cache_dir='/tmp/cache'):
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)
        self.app = app
        self.cache = FileSystemCache(cache_dir)
        self.start_server_response = None
        self.content_key = None
        self.header_key = None
        self.status_key = None
        self.status = None
        self.headers = None

    def __call__(self, environ, start_response):
        self.start_server_response = start_response

        # get keys content, header and status
        self.content_key = environ['PATH_INFO']
        if environ.get('QUERY_STRING'):
            self.content_key = '%s?%s' % (self.content_key,
                                          environ['QUERY_STRING'])
        self.header_key = '%s|%s' % (self.content_key, 'header')
        self.status_key = '%s|%s' % (self.content_key, 'status')

        # get cached response
        keys = (self.content_key, self.header_key, self.status_key)
        content, headers, status = self.cache.get_many(*keys)

        if (content is not None
           and headers is not None
           and status is not None):
            # return cached response
            self.start_server_response(status, headers)
            print 'return cached'
            return content
        else:
            # call app and cache the response
            content = self.app(environ, self.start_response)
            if self.do_cache():
                self.cache.set_many({self.content_key: list(content),
                                     self.header_key: self.headers,
                                     self.status_key: self.status})
                print 'do cache'
            return content

    def start_response(self, status, response_headers, exc_info=None):
        self.status = status
        self.headers = response_headers
        self.start_server_response(status, response_headers, exc_info)

    def do_cache(self):
        if 200 <= int(self.status.split(' ')[0]) < 300:
            return True
        else:
            return False
