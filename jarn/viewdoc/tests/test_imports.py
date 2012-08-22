# This test fails when run in a virtualenv under Python 3.2.3

# Adding these libraries fixes the test:

# functools.py
# heapq.py
# bisect.py
# weakref.py
# reprlib.py

import unittest
import sys
import subprocess


def test_missing_libs_break_stdout_encoding_when_writing_to_pipe():
    # ImportErrors cause an unfortunate codepath to be taken in
    # textiowrapper_init(). See Modules/_io/textio.c:900
    # The result is a stdout encoding of 'ascii' for the subprocess
    process = subprocess.Popen(
        [sys.executable, '-c', 'import sys; print(sys.stdout.encoding)'],
        stdout=subprocess.PIPE,
        )
    out, err = process.communicate()
    encoding = out.strip()

    if sys.version_info < (3,):
        # In Python 2 the encoding is always None
        assert encoding == 'None', \
            "%r != 'None'" % (encoding,)
    else:
        # In Python 3 the encoding should match the main
        # process' encoding
        encoding = encoding.decode('ascii')
        assert encoding == sys.stdout.encoding, \
            '%r != %r' % (encoding, sys.stdout.encoding)


class StdoutEncodingTests(unittest.TestCase):

    def test_missing_libs_break_stdout_encoding_when_writing_to_pipe(self):
        test_missing_libs_break_stdout_encoding_when_writing_to_pipe()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


if __name__ == '__main__':
    test_missing_libs_break_stdout_encoding_when_writing_to_pipe()

