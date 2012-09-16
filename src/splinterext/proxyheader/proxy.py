# -*- coding: utf-8 -*-
"""The proxy"""

from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import is_hop_by_hop
import multiprocessing
import atexit
import httplib
import atexit

from utils import Singleton


class CustomHeadersManager(object):
    """The object that helps playing with HTTP headers
    """
    __metaclass__ = Singleton

    _capture_next_response = False
    _response_headers = {}
    _extra_req_headers = {}

    def set_header(self, name, value):
        """Adds or sets a request header
        """
        self._extra_req_headers[name.lower()] = value
        return

    def unset_header(self, name):
        """Removes a custom request header
        """
        name = name.lower()
        if name in self._extra_req_headers:
            del self._extra_req_headers[name]
        return

    def pre_hook(self, req_headers):
        req_headers.update(self._extra_req_headers)
        return

    def capture_response_headers(self):
        self._capture_next_response = True
        return

    def get_response_header(self, name):
        return self._response_headers.get(name.lower())

    def post_hook(self, resp_headers):
        if self._capture_next_response:
            self._capture_next_response = False
            self._response_headers.clear()
            # Making a deep copy
            for name, value in resp_headers:
                name = name.lower()
                if name in self._response_headers:
                    self._response_headers[name] += ',' + value
                else:
                    self._response_headers[name] = value
        return


# Global object for setting/capturing headers
custom_headers = CustomHeadersManager()


# FIXME: using an HTTPSConnection does not work as expected
scheme2connection = {
    # {scheme: connection class, ...}
    'http': httplib.HTTPConnection,
    'https': httplib.HTTPSConnection
    }



def iterstreamer(fp):
    """Yields file content by 1024 bytes chunks
    """
    while True:
        chunk = fp.read(1024)
        if len(chunk) == 0:
            raise StopIteration
        yield chunk

def proxy_app(environ, start_response):
    """Formards the request to the real server
    """
    # Rebuilding the request headers from environ
    req_headers = {}
    not_relayed_headers = ('HTTP_ACCEPT_ENCODING', 'HTTP_HOST', 'HTTP_PROXY_CONNECTION')
    for name, value in ((name, value) for name, value in environ.iteritems()
                        if name.startswith('HTTP_') and name not in not_relayed_headers):
        # HTTP_XX_XX -> xx-xx
        name = '-'.join(w.lower() for w in name[5:].split('_'))
        req_headers[name] = value

    # Some headers are not prefixed with HTTP

    for name in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
        value = environ.get(name, None)
        if value:
            name = '-'.join(w.lower() for w in name.split('_'))
            req_headers[name] = value

    # Add or change headers
    custom_headers.pre_hook(req_headers)

    # Proxying to the destination server
    scheme = environ.get('wsgi.url_scheme', 'http')
    connection_class = scheme2connection.get(scheme, httplib.HTTPConnection)
    conn = connection_class(environ['HTTP_HOST'])
    req_meth = environ['REQUEST_METHOD']
    conn.request(req_meth, '{0[PATH_INFO]}?{0[QUERY_STRING]}'.format(environ), headers=req_headers)

    if req_meth == 'POST':
        # We need to relay the body too
        input_ = environ['wsgi.input']
        length = int(environ.get('CONTENT_LENGTH', '0'))
        payload = input_.read(length)  # Oops, could be a biiiig file
        conn.send(payload)

    # Transform / relay the response
    response = conn.getresponse()
    txt_status = httplib.responses.get(response.status, "Unknown status {0}".format(response.status))
    status = '{0} {1}'.format(response.status, txt_status)

    # Remove so-called "hop by hop" headers
    resp_headers = [(n, v)  for n, v in response.getheaders() if not is_hop_by_hop(n)]

    # Notify response headers if required
    custom_headers.post_hook(resp_headers)

    # Replying to browser
    start_response(status, resp_headers)
    return iterstreamer(response)


class ProxyWSGIRequestHandler(WSGIRequestHandler):
    """We don't want anything in the console while the proxy is running
    """
    def log_request(self, code='-', size='-'):
        # Intentionally empty
        return


class ProxyController(object):
    """Creates, activates and kills the proxy.
    """
    __metaclass__  = Singleton
    _started = False

    def start(self, port):
        if not self._started:
            server = make_server('', port, proxy_app, handler_class=ProxyWSGIRequestHandler)
            self.server_process = multiprocessing.Process(target=server.serve_forever)
            self.server_process.start()
            self._started = True
        return

    def stop(self):
        if self._started:
            self.server_process.terminate()
            self.server_process.join()
            del self.server_process
            self._started = False
        return

proxy_controller = ProxyController()

atexit.register(proxy_controller.stop)
