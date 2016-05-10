import boto
import boto.utils
import hashlib
import os
import pkg_resources
import pickle
import sys
import syslog
import time
from monitoring import VERSION

pkg_resources.require('boto>=2.33.0')

META_DATA_CACHE_DIR = os.environ.get('AWS_EC2CW_META_DATA', '/tmp/aws-mon')
META_DATA_CACHE_TTL = os.environ.get('AWS_EC2CW_META_DATA_TTL', 21600)


class FileCache:
    CLIENT_NAME = None

    def __init__(self, fnc):
        self.fnc = fnc
        if not os.path.exists(META_DATA_CACHE_DIR):
            os.makedirs(META_DATA_CACHE_DIR)

    def __call__(self, *args, **kwargs):
        sig = ":".join([VERSION, str(self.fnc.__name__), str(args), str(kwargs)])

        filename = os.path.join(META_DATA_CACHE_DIR, '{0}-{1}.bin'
                                .format(self.CLIENT_NAME,
                                        hashlib.md5(sig).hexdigest()))

        if os.path.exists(filename):
            mtime = os.path.getmtime(filename)
            now = time.time()
            if mtime + META_DATA_CACHE_TTL > now:
                with open(filename, 'rb') as f:
                    return pickle.load(f)

        tmp = self.fnc(*args, **kwargs)
        with open(filename, 'wb') as f:
            os.chmod(filename, 0600)
            pickle.dump(tmp, f)

        return tmp


def log_error(message, use_syslog):
    if use_syslog:
        syslog.syslog(syslog.LOG_ERR, message)
    else:
        print >> sys.stderr, 'ERROR: ' + message


@FileCache
def get_metadata():
    metadata = boto.utils.get_instance_metadata(timeout=1, num_retries=2)
    if not metadata:
        raise ValueError('Cannot obtain EC2 metadata.')
    return metadata
