import urllib.request
import urllib.parse
import http.cookiejar
from html.parser import HTMLParser


class TokenParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.token = None

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            if len(attrs) == 0:
                pass
            else:
                if ('name', 'token') in attrs and ('type', 'hidden') in attrs:
                    self.token = attrs[2][1]


class ContentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.content = ''
        self.trigger = False
    
    def handle_starttag(self, tag, attrs):
        if tag != 'textarea':
            return
        if ('id', 'mdeditor') in attrs and ('name', 'content') in attrs:
            self.trigger = True
            return
    
    def handle_endtag(self, tag):
        if tag == 'textarea' and self.trigger:
            self.trigger = False

    def handle_data(self, data):
        if self.trigger:
            self.content = data


token_parser = TokenParser()
content_parser = ContentParser()


class ReportSender:
    def __init__(self, username, password):
        # general cookie jar
        cj = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(handler)
        self.opener = opener
        
        self.login(username, password)

    def parse_token(self, res):
        token_parser.feed(res)
        token_parser.close()
        return token_parser.token

    def parse_content(self, res):
        content_parser.feed(res)
        content_parser.close()
        return content_parser.content

    def login(self, username, password):
        url = 'https://at.twtstudio.com/login'

        token_res = self.opener.open(url)
        token = self.parse_token(token_res.read().decode('utf-8'))
        if not token:
            raise TypeError('token not found')
        data = {
            'token': token,
            'username': username,
            'password': password
        }
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        login_req = urllib.request.Request(url, data=post_data, method='POST')
        self.opener.open(login_req)

    def get_content(self):
        url = 'https://at.twtstudio.com/report/write'
        request = urllib.request.Request(url)
        response = self.opener.open(request).read().decode('utf-8')
        write_token = self.parse_token(response)
        old_content = self.parse_content(response)
        self.old_content = old_content
        self.write_token = write_token

    def write(self, content):
        url = 'https://at.twtstudio.com/report'
        data = {
            'token': self.write_token,
            'content': content
        }
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, data=post_data, method='POST')
        self.opener.open(request)
    