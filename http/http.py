import re

CRLF = '\r\n'

class HttpParser:
    def __init__(self, raw):
        self._is     = None
        self.version = None
        self.headers = None
        self.body    = None
        self.parser(raw)

    def parser(self, raw):
        info, body = raw.split(CRLF*2, 1)
        infoline, headers = info.split(CRLF, 1)
        self._http_info(infoline)
        self._header_parser(headers)
        self._body_parser(body)

    def _http_info(self, line):
        res = re.match(
            '^(?P<method>[A-Z]+) (?P<path>/.*) HTTP/(?P<version>[0-9]\.[0-9])', line)
        if res:
            self._is     = 'request'
            self.version = res.group('version')
            self.method  = res.group('method')
            self.path    = res.group('path')
            return
        res = re.match(
            '^HTTP/(?P<version>[0-9]\.[0-9]) (?P<status>[0-9]+) (?P<message>[a-zA-Z0-9]+)', line)
        if res:
            self._is     = 'response'
            self.version = res.group('version')
            self.status  = res.group('status')
            self.message = res.group('message')

    def _header_parser(self, raw):
        self.headers = dict()
        for line in raw.splitlines():
            key, value = line.split(': ')
            self.headers.update({key:value})

    def _body_parser(self, raw):
        self.body = raw

    def print_info(self):
        if self._is == 'request':
            print(self.version, self.method, self.path)
        if self._is == 'response':
            print(self.version, self.status, self.message)
        else: return None
        print(self.headers)
        print(self.body)
