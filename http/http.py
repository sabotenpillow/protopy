import re
import gzip

CRLF   = '\r\n'
B_CRLF = b'\r\n'

class HttpParser:
    def __init__(self, raw):
        self._is     = None
        self.version = None
        self.headers = None
        self.body    = None
        ## Request  : has "method", "path" too
        ## Response : has "status", "message" too
        self.parser(raw)

    def parser(self, raw):
        info, body = bytes.split(raw, B_CRLF*2, 1)
        infoline, headers = info.decode().split(CRLF, 1)
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
        if 'Content-Encoding' in self.headers:
            self.headers['Content-Encoding'] \
                = [x.strip() for x in self.headers['Content-Encoding'].split(',')]
        if 'Transfer-Encoding' in self.headers:
            self.headers['Transfer-Encoding'] \
                = [x.strip() for x in self.headers['Transfer-Encoding'].split(',')]

    def _body_parser(self, raw):
        self.body = raw.decode()

    def print_info(self):
        if   self._is == 'request':
            print(self.version, self.method, self.path)
        elif self._is == 'response':
            print(self.version, self.status, self.message)
        else: return None
        print(self.headers)
        print(self.body)

    def get_raw(self):
        if   self._is == 'request':
            infoline = "{0} {1} HTTP/{2}".format(self.method, self.path, self.version)
        elif self._is == 'response':
            infoline = "HTTP/{0} {1} {2}".format(self.version, self.status, self.message)
        raw = infoline + CRLF \
            + CRLF.join([
                k+': '+v if k!='Content-Encoding' and k!='Transfer-Encoding'
                else k+': '+', '.join(v) for k, v in self.headers.items()]) \
            + CRLF*2 + self.body
        return raw
