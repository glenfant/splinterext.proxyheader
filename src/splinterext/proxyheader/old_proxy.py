# -*- coding: utf-8 -*-
"""The proxy"""
# Most code of this module is stolen from
# http://pypi.python.org/pypi/ProxyHTTPServer/0.0.1 but this is not a setuptools
# aware stuff and its author Davide Rognoni <davide.rognoni@gmail.com> has a
# fake mail address.

import BaseHTTPServer
import SocketServer
import httplib
import urllib
import urlparse
import threading
from collections import defaultdict
import atexit


class CustomHeaders(object):
    """The object that helps playing with HTTP headers
    """
    _capture_next_response = False
    _response_headers = defaultdict(list)

    def capture_next_response(self):
        self._capture_next_response = True

    def capture_response_headers(self, response):
        if self._capture_next_response:
            _capture_next_response = False
            self._response_headers.clear()
            raw_headers = response.headers
            # Making a deep copy
            for name in raw_headers.keys():
                self._response_headers[name] = raw_headers.getList(name)[:]
        return

    def add_extra_headers_to(self, request):
        # FIXME: ZZZ
        return

    def add_extra_request_header(self, name, value):
        """From user side"""
        # FIXME: ZZZ
        return

# Global object for setting/capturing headers
custom_headers = CustomHeaders()


class ProxyHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def doCommon(self):
        global custom_headers

        req = Request(self)
        req.delHeaders("accept-encoding", "host", "proxy-connection")
        # Custom request headers
        custom_headers.add_extra_headers_to(req)

        res = req.getResponse()
        res.delHeader("transfer-encoding")
        # Capture response headers
        custom_headers.capture_response_headers(res)
        res.toClient()

    def do_GET(self):
        self.doCommon()

    def do_POST(self):
        self.doCommon()

# FIXME: using an HTTPSConnection does not work as expected
scheme2connection = {
    # {scheme: connection class, ...}
    'http': httplib.HTTPConnection,
    'https': httplib.HTTPSConnection
    }


class Request(object):
    def __init__(self, proxy):
        self.proxy = proxy
        self.host = proxy.headers.getheader("host")
        self.command = proxy.command
        self.path = proxy.path
        self.headers = proxy.headers.dict

        # HTTPConnection
        scheme = urlparse.urlparse(proxy.raw_requestline.split()[1]).scheme
        connection_class = scheme2connection.get(scheme, httplib.HTTPConnection)
        self.conn = connection_class(self.host)

        if self.command == "POST":
            self.body = self.proxy.rfile.read(
                int(self.proxy.headers.getheader("content-length"))
                )
        else:
            self.body = None

    def getHeader(self, k):
        if k in self.headers:
            return self.headers[k]
        else:
            return None

    def setHeader(self, k, v):
        self.headers[k] = v

    def setHeaders(self, dict_):
        for k, v in dict_.iteritems():
            self.setHeader(k, v)

    def delHeader(self, k):
        if k in self.headers:
            del self.headers[k]

    def delHeaders(self, *list_):
        for l in list_:
            self.delHeader(l)

    def bodyDecode(self):
        m = MapList()
        for b in self.body.split("&"):
            for p in b.split("="):
                if p != "":
                    m.add(urllib.unquote_plus(p[0]), urllib.unquote_plus(p[1]))
        return m

    def bodyEncode(self, mapList):
        body = ""
        for k in mapList.keys():
            for l in mapList.getList(k):
                body += "%s=%s&" % (urllib.quote_plus(k),
                                    urllib.quote_plus(l))
        if body == "":
            self.body = None
        else:
            self.body = body[:-1]

    def getResponse(self):
        if self.body:
            self.headers["content-length"] = str(len(self.body))
            self.conn.request("POST", self.path, self.body, self.headers)
        else:
            self.conn.request("GET", self.path, headers=self.headers)

        return Response(self.proxy, self.conn.getresponse())


class Response(object):
    def __init__(self, proxy, server):
        self.proxy = proxy
        self.server = server
        self.status = server.status
        self.body = server.read()

        self.headers = MapList()
        for l in server.getheaders():
            self.headers.add(l[0], l[1])

    def getHeader(self, k, index=-1):
        if self.headers.hasKey(k, index):
            return self.headers.get(k, index)
        else:
            return None

    def setHeader(self, k, v, index=-1):
        self.headers.set(k, v, index)

    def addHeader(self, k, v):
        self.headers.add(k, v)

    def addHeaders(self, dict_):
        for name, value in dict.iteritems():
            self.setHeader(name, value)

    def delHeader(self, k):
        if self.headers.hasKey(k):
            self.headers.delMap(k)

    def delHeaders(self, *names):
        for name in names:
            self.delHeader(name)

    def toClient(self):
        self.proxy.send_response(self.status)
        for k in self.headers.keys():
            for l in self.headers.getList(k):
                self.proxy.send_header(k, l)
        self.proxy.end_headers()
        self.proxy.wfile.write(self.body)


class MapList(object):
    def __init__(self):
        self.map = {}

    def __str__(self):
        return str(self.map)

    def add(self, name, value):
        if name in self.map:
            self.map[name].append(value)
        else:
            self.map[name] = [value]

    def set(self, name, value, index=-1):
        if name in self.map:
            self.map[name][index] = value
        else:
            self.map[name] = [value]

    def get(self, name, index=-1):
        return self.map[name][index]

    def getList(self, name):
        return self.map[name]

    def delMap(self, name):
        if name in self.map:
            del self.map[name]

    def delList(self, name, index=-1):
        if name in self.map:
            del self.map[name][index]

    def hasKey(self, name, index=-1):
        if name in self.map:
            values = self.map[name]
            if index < 0:
                index += 1
            if len(values) > abs(index):
                return True
        return False

    def keys(self):
        return self.map.keys()

    def mapSize(self):
        return len(self.map)

    def listSize(self, name):
        if name in self.map:
            return len(self.map[name])
        else:
            return 0

    def size(self):
        size = 0
        for _ignore, value in self.map.iteritems():
            size += len(value)
        return size


class ThreadingHTTPServer(SocketServer.ThreadingTCPServer, BaseHTTPServer.HTTPServer):
    pass


class ProxyController(object):
    """Creates, activates and kills the proxy. Inspiration from
    http://docs.python.org/library/socketserver.html#asynchronous-mixins
    """
    def __init__(self, port):
        self.server = ThreadingHTTPServer(('', port), ProxyHTTPRequestHandler)

    def start(self):
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        return

    def stop(self):
        self.server.shutdown()
        return

proxy_controller = None


def make_proxy_controller(port):
    global proxy_controller
    proxy_controller = ProxyController(port)


def shutdown_proxy_controller():
    global proxy_controller
    if proxy_controller is not None:
        proxy_controller.stop()

atexit.register(shutdown_proxy_controller)
