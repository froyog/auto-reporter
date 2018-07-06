import os
import stat
import subprocess
import sys

def main():
    git_dir = subprocess.check_output(['git', 'rev-parse', '--git-dir'])
    hook_file_path = os.path.join(
        os.path.abspath(git_dir.strip().decode('utf-8')), 'hooks', 'pre-push'
    )

    with open(hook_file_path, 'w') as fd:
        content = '%s -c "import sys; import os; import twt-auto-reporter.hook; sys.exit(twt-auto-reporter.main(%s, os.path.split(os.getcwd())[1]))" $@\n' % (sys.executable, sys.argv[1:])
        fd.write(content)
    os.chmod(hook_file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    sys.stdout.write('Auto report installed.\n')
