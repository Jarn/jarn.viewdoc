import sys
import os
import unittest
import tempfile
import shutil
import functools

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

from os.path import realpath, isdir


class ChdirStack(object):
    """Stack of current working directories."""

    def __init__(self):
        self.stack = []

    def __len__(self):
        return len(self.stack)

    def push(self, dir):
        """Push cwd on stack and change to 'dir'.
        """
        self.stack.append(os.getcwd())
        os.chdir(dir or os.getcwd())

    def pop(self):
        """Pop dir off stack and change to it.
        """
        if len(self.stack):
            os.chdir(self.stack.pop())


class JailSetup(unittest.TestCase):
    """Manage a temporary working directory."""

    dirstack = None
    tempdir = None

    def setUp(self):
        self.dirstack = ChdirStack()
        try:
            self.tempdir = realpath(self.mkdtemp())
            self.dirstack.push(self.tempdir)
        except:
            self.cleanUp()
            raise

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        if self.dirstack is not None:
            while self.dirstack:
                self.dirstack.pop()
        if self.tempdir is not None:
            if isdir(self.tempdir):
                shutil.rmtree(self.tempdir)

    def mkdtemp(self):
        return tempfile.mkdtemp()

    def mkfile(self, name, body=''):
        with open(name, 'wt') as file:
            file.write(body)


def quiet(func):
    """Decorator swallowing stdout and stderr output.
    """
    def wrapper(*args, **kw):
        saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StringIO()
        try:
            return func(*args, **kw)
        finally:
            sys.stdout, sys.stderr = saved

    return functools.wraps(func)(wrapper)

