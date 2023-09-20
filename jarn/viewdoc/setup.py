# 'from jarn.viewdoc import setup; setup.run(%(args)r)'

import sys
import os
import glob

from os.path import isdir, join, exists


def no_walk_revctrl(dirname=''):
    """Return empty list.
    """
    # Returning a non-empty list prevents egg_info from reading the
    # existing SOURCES.txt
    return ['']


def cleanup_pycache():
    """Remove .pyc files we leave around because of import.
    """
    try:
        for file in glob.glob('setup.py[co]'):
            os.remove(file)
        if isdir('__pycache__'):
            for file in glob.glob(join('__pycache__', 'setup.*.py[co]')):
                os.remove(file)
            if not glob.glob(join('__pycache__', '*')):
                os.rmdir('__pycache__')
    except (IOError, OSError):
        pass


def run(args):
    """Run setup.py with monkey patches applied.
    """
    # Set log level INFO in setuptools >= 60.0.0 with local distutils
    import setuptools
    import distutils
    if hasattr(distutils.log, 'set_verbosity'):
        distutils.log.set_verbosity(1)

    # Required in setuptools >= 60.6.0, <= 60.9.1
    import distutils.dist
    if hasattr(distutils.dist.log, 'set_verbosity'):
        distutils.dist.log.set_verbosity(1)

    import setuptools.command.egg_info
    setuptools.command.egg_info.walk_revctrl = no_walk_revctrl

    sys.argv = ['setup.py'] + args
    try:
        if exists('setup.py'):
            import setup
        else:
            setuptools.setup()
    finally:
        cleanup_pycache()

