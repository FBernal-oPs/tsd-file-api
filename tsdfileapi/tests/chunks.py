
"""
Exploring Transfer-Encoding: chunked with a minimal python client.

From: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding

Data is sent in a series of chunks. The Content-Length header is omitted in this
case and at the beginning of each chunk you need to add the length of the current
chunk in hexadecimal format, followed by '\r\n' and then the chunk itself, followed
by another '\r\n'.

The terminating chunk is a regular chunk, with the exception that its length is zero.
It is followed by the trailer, which consists of a (possibly empty) sequence of
entity header fields.

E.g.

HTTP/1.1 200 OK
Content-Type: text/plain
Transfer-Encoding: chunked

7\r\n
Mozilla\r\n
9\r\n
Developer\r\n
7\r\n
Network\r\n
0\r\n
\r\n

tornado
so with tornado it _just works_ - but not the naive impl
the async method write data to the file, while waiting for the rest
this is _exactly what the video streaming needs.
behind nginx you need to set the following:
proxy_http_version 1.1;
proxy_request_buffering off;

"""
import logging
import httplib
import requests
import string
import time
import sys
import json
import os

httplib.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# TODO get from config
BASE_URL = 'http://localhost'
PORT = '8888'
URL = BASE_URL + ':' + PORT

def create_test_file(filename):
    with open(filename, 'w+') as f:
        f.write('x,y')
        f.write('5,6')
        f.write('7,8')

def lazy_file_reader(filename):
    with open('blamo.csv', 'r+') as f:
        while True:
            line = f.readline()
            if line == '':
                break
            else:
                yield line

def get_token():
    resp = requests.post(URL + '/upload_token',
        data=json.dumps({'email':'health@check.local', 'pw': 'something_healthy'}),
        headers={'Content-Type': 'application/json'})
    return json.loads(resp.text)['token']

def test_streaming(token_should_be_invalid=False):
    src_filename = 'test-file'
    dest_filename = 'created-file'
    try:
        create_test_file(src_filename)
        token = get_token()
        if token_should_be_invalid:
            token = token[:-1]
        headers = { 'X-Filename': dest_filename, 'Authorization': 'Bearer ' + token }
        resp = requests.post(URL + '/stream', data=lazy_file_reader(src_filename), headers=headers)
        print resp.text
    except Exception:
        raise Exception
    finally:
        os.remove(src_filename)

test_streaming()