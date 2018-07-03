#!/usr/bin/env python

import sys
import subprocess

for line in sys.stdin:
    local_ref, local_sha1, remote_ref, remote_sha1 = line.strip().split(' ')
    raw_messages = subprocess.check_output(
        ['git', 'show', '--format=%s', '-s', "%s..%s" % (remote_sha1, local_sha1)]
    )
    messages = raw_messages.decode('utf-8').splitlines()[0:-1]
    print(messages)

sys.exit(1)

token = 'A0kdLSU9bhTXDj5d7kpe9eRzuEBEkBLAOScScansDy4'
content = ''