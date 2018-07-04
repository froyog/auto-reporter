#!/usr/bin/env python

import sys
import subprocess
import getopt
import re
from sender import ReportSender

commit_msgs = []
for line in sys.stdin:
    local_ref, local_sha1, remote_ref, remote_sha1 = line.strip().split(' ')
    raw_messages = subprocess.check_output(
        ['git', 'show', '--format=%s', '-s', "%s..%s" % (remote_sha1, local_sha1)]
    )
    commit_msgs = raw_messages.decode('utf-8').splitlines()[0:-1]

display_name = ''
username = ''
password = ''
def main(argv):
    try:
        opts, args = getopt.getopt(
            argv, 
            'hd:u:p:', 
            ['help', 'display-name=', 'username=', 'password=', 'thanks']
        )
    except getopt.GetoptError:
        print('Unknown option')
        print('Type install-auto-reporter --help for more information.')

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('Usage:')
            return
        if opt in ('-d', '--display-name'):
            display_name = opt
        if opt in ('-u', '--username'):
            username = opt
        if opt in ('-p', '--password'):
            password = opt
        if opt == '--thanks':
            print('mua')
            return

title = '## %s\r\n' % display_name

AT = ReportSender(username, password)
AT.get_content()
report_array = re.split(r'## %s\r\n' % display_name, AT.old_content)

body_string = ''
for commit_msg in commit_msgs:
    body_string = body_string + '- %s\r\n' % commit_msg

if len(report_array) == 1:
    # no title found
    # append title
    report_array.append('\r\n%s' % title)
    report_array.append(body_string)
elif len(report_array) == 2:
    # found title
    report_array.insert(1, title)
    report_array.insert(2, body_string)
else:
    raise ValueError('strange thing happend')

AT.write(''.join(report_array))