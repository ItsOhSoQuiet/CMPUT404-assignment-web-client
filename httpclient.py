#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
    
    # Take the url, and separate it into its different components
    # Took from: https://docs.python.org/3/library/urllib.parse.html
    def parse_url(self, url):
        parsed_url = urllib.parse.urlparse(url)
        port = parsed_url.port
        host = parsed_url.hostname

        # get the scheme, if none, make it https
        scheme = parsed_url.scheme
        if scheme == '':
            scheme = 'https'
        
        # get the path, if no path, then make it root
        path = parsed_url.path
        if path == '':
            path = '/'
        
        return port, host, scheme, path


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    # Instead of getting data from the socket,
    # I am using this to get headers from arguments
    # Learned about urlencode from here: 
    # https://docs.python.org/3/library/urllib.parse.html
    def get_headers(self,data):
        headers = urllib.parse.urlencode(data)
        return headers

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        port, host, scheme, path = self.parse_url(url)

        # read the data from the URL in the request.
        # First, we need to make a socket to connect to the 
        # URL in question.
        self.connect(host, port)

        # Then we have to form a request
        # How to do that taken from here: 
        # https://www.tutorialspoint.com/http/http_requests.htm
        request = "GET " + path + " HTTP/1.1\r\n"
        request += "Host: " + host + "\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n\r\n"
        
        # Now, send the request to the socket
        self.sendall(request)

        # Then, read all of the data from the socket
        request_data = self.recvall(self.socket)

        # Always remember to close the socket!
        self.close()
        
        code = self.get_code(request_data)
        body = self.get_body(request_data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        port, host, scheme, path = self.parse_url(url)

        # read the data from the URL in the request.
        # First, we need to make a socket to connect to the 
        # URL in question.
        self.connect(host, port)

        # Then we have to form a request
        # How to do that taken from here: 
        # https://www.tutorialspoint.com/http/http_requests.htm
        # Also need to account for any arguments that could be a query.
        request = "POST " + path + " HTTP/1.1\r\n"
        request += "Host: " + host + "\r\n"
        if args is None:
            request += "Content-Length: 0\r\n"
            headers = ""
        else:
            # Arguments are a dictionary, need to parse them
            # so that they can become headers.
            headers = self.get_headers(args)
            request += "Content-Length: " + str(len(headers)) + "\r\n"
        request += "Content-Type: application/x-www-form-urlencoded"
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n\r\n"
        request += headers

        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
