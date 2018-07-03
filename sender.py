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
    def __init__(self, username, password, content=''):
        # general cookie jar
        cj = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(handler)
        self.opener = opener
        
        self.login(username, password)
        self.write(content)

    def get_token(self, res):
        token_parser.feed(res)
        token_parser.close()
        return token_parser.token

    def get_content(self, res):
        content_parser.feed(res)
        content_parser.close()
        return content_parser.content

    def login(self, username, password):
        url = 'https://at.twtstudio.com/login'

        token_res = self.opener.open(url)
        token = self.get_token(token_res.read().decode('utf-8'))
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

    def write(self, content):
        write_url = 'https://at.twtstudio.com/report/write'
        write_req = urllib.request.Request(write_url)
        write_res = self.opener.open(write_req)
        write_res = write_res.read().decode('utf-8')

        write_token = self.get_token(write_res)
        old_content = self.get_content(write_res)
        new_content = old_content + content

        report_url = 'https://at.twtstudio.com/report'
        data = {
            'token': write_token,
            'content': new_content
        }
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        report_req = urllib.request.Request(report_url, data=post_data, method='POST')
        self.opener.open(report_req)
    