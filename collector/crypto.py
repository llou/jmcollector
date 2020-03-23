import sys
import hashlib
import platform
from subprocess import run, PIPE
from utils import platform


raw_platform = platform.platform()

if raw_platform[0:5] == "macOS":
    PLATFORM = "MACOS"
elif raw_platform[0:5] == "Linux":
    PLATFORM = "LINUX"
elif raw_platform[0:7] == "WINDOWS":
    PLATFORM = "WINDOWS"
else:
    print("System Unknown")
    sys.exit(1)


def get_sha1_file(path):
    if PLATFORM in ["LINUX","MACOS"]:
        if PLATFORM == "LINUX":
            p = run(["/usr/bin/shasum", path], stdout=PIPE, stderr=PIPE)
        elif PLATFORM == "MACOS":
            p = run(["/usr/bin/shasum", "-a", "1", path], stdout=PIPE, stderr=PIPE)
        if p.returncode:
            print("Error processing file %s." % path)
            sys.exit(1)
        return p.stdout.decode("utf-8").split(" ")[0]
    else:
        BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
        sha1 = hashlib.sha1()
        with open(sys.argv[1], 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

def get_sha1_var(data):
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()

