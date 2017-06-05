
import os
from gzip import GzipFile
from io import BytesIO
import threading
import fcntl

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
    def __init__(self, app, cache_dir='/tmp/cache', lock_file=None):
        if not os.path.isdir(cache_dir):
            os.mkdir(cache_dir)
        self.app = app
        self.cache = FileSystemCache(cache_dir, default_timeout=600)
        self.t_local = threading.local()
        if lock_file is not None:
            lock_file = os.path.abspath(os.path.realpath(lock_file))
        else:
            lock_file = '/tmp/cache.lock'

        self.lock_file = open(lock_file, 'wb+')
        self.t_lock = threading.Lock()

    def __call__(self, environ, start_response):
        self.t_local.start_server_response = start_response

        # get keys content, header and status
        self.t_local.content_key = environ['PATH_INFO']
        if environ.get('QUERY_STRING'):
            self.t_local.content_key = '%s?%s' % (self.t_local.content_key,
                                                  environ['QUERY_STRING'])
        self.t_local.header_key = '%s|%s' % (self.t_local.content_key, 'header')
        self.t_local.status_key = '%s|%s' % (self.t_local.content_key, 'status')

        # get cached response
        keys = (self.t_local.content_key, self.t_local.header_key,
                self.t_local.status_key)
        with self.t_lock:
            try:
                fcntl.lockf(self.lock_file, fcntl.LOCK_SH)
                content, headers, status = self.cache.get_many(*keys)
            finally:
                fcntl.lockf(self.lock_file, fcntl.LOCK_UN)

        if (content is not None
           and headers is not None
           and status is not None):
            # return cached response
            self.t_local.start_server_response(status, headers)
            return content
        else:
            # call app and cache the response
            content = self.app(environ, self.start_response)
            if self.do_cache():
                content = list(content)
                cached = {self.t_local.content_key: content,
                          self.t_local.header_key: self.t_local.headers,
                          self.t_local.status_key: self.t_local.status}
                with self.t_lock:
                    try:
                        fcntl.lockf(self.lock_file, fcntl.LOCK_EX)
                        self.cache.set_many(cached)
                    finally:
                        fcntl.lockf(self.lock_file, fcntl.LOCK_UN)
            return content

    def start_response(self, status, response_headers, exc_info=None):
        self.t_local.status = status
        self.t_local.headers = response_headers
        self.t_local.start_server_response(status, response_headers, exc_info)

    def do_cache(self):
        if 200 <= int(self.t_local.status.split(' ')[0]) < 300:
            return True
        else:
            return False
