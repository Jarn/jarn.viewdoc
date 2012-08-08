from __future__ import with_statement

import locale
locale.setlocale(locale.LC_ALL, '')

import pkg_resources
__version__ = pkg_resources.get_distribution('jarn.viewdoc').version

import sys
import os
import getopt
import webbrowser
import ConfigParser
import functools

from os.path import abspath, expanduser, dirname, basename
from os.path import split, join, isdir, isfile
from subprocess import Popen, PIPE
from contextlib import closing
from docutils.core import publish_string

VERSION = "jarn.viewdoc %s" % __version__
USAGE = "Try 'viewdoc --help' for more information"

HELP = """\
Usage: viewdoc [options] [rst-file|egg-dir]

Python documentation viewer

Options:
  -s style, --style=style, or --style
                      Select the custom style added to the HTML output.
                      Used to override the configuration file setting of
                      the same name.

  -l, --list-styles   List available styles and exit.
  -h, --help          Print this help message and exit.
  -v, --version       Print the version string and exit.

  rst-file            reST file to view.
  egg-dir             Package whose long description to view. Defaults to
                      the current working directory.
"""

PLAIN = """\
<style type="text/css">
body { margin-left: 10em; margin-right: 10em; }
</style>
"""

PYPI = """\
<link rel="stylesheet" href="http://www.python.org/styles/styles.css" type="text/css" />
<style type="text/css">
body { margin-left: 10em; margin-right: 10em; font-size: 95%; }
a:link { text-decoration: none; color: #0000aa; }
a:visited { text-decoration: none; color: #551a8b; }
a.reference { border-bottom: 1px dashed #cccccc; }
</style>
"""

SMALL = """\
<link rel="stylesheet" href="http://www.python.org/styles/styles.css" type="text/css" />
<style type="text/css">
body { margin-left: 10em; margin-right: 10em; font-size: 90%; }
a:link { text-decoration: none; color: #0000aa; }
a:visited { text-decoration: none; color: #551a8b; }
a.reference { border-bottom: 1px dashed #cccccc; }
</style>
"""

DEFAULT_CONFIG = """\
[viewdoc]
style = pypi

[styles]
plain =
    <style type="text/css">
    body { margin-left: 10em; margin-right: 10em; }
    </style>
pypi =
    <link rel="stylesheet" href="http://www.python.org/styles/styles.css" type="text/css" />
    <style type="text/css">
    body { margin-left: 10em; margin-right: 10em; font-size: 95%; }
    a:link { text-decoration: none; color: #0000aa; }
    a:visited { text-decoration: none; color: #551a8b; }
    a.reference { border-bottom: 1px dashed #cccccc; }
    </style>
small =
    <link rel="stylesheet" href="http://www.python.org/styles/styles.css" type="text/css" />
    <style type="text/css">
    body { margin-left: 10em; margin-right: 10em; font-size: 90%; }
    a:link { text-decoration: none; color: #0000aa; }
    a:visited { text-decoration: none; color: #551a8b; }
    a.reference { border-bottom: 1px dashed #cccccc; }
    </style>
"""

if sys.version_info[0] >= 3:
    # Open files in UTF-8
    open = functools.partial(open, encoding='utf-8')


def msg_exit(msg, rc=0):
    """Print msg to stdout and exit with rc.
    """
    print msg
    sys.exit(rc)


def err_exit(msg, rc=1):
    """Print msg to stderr and exit with rc.
    """
    print >>sys.stderr, msg
    sys.exit(rc)


def warn(msg):
    """Print warning msg to stderr.
    """
    print >>sys.stderr, 'WARNING:', msg


class changedir(object):
    """Change directory."""

    def __init__(self, dir):
        self.old = os.getcwd()
        self.dir = dir or self.old

    def __enter__(self):
        os.chdir(self.dir)

    def __exit__(self, *ignored):
        os.chdir(self.old)


class Python(object):

    def __init__(self):
        self.python = sys.executable
        self.version_info = sys.version_info

    def __str__(self):
        return self.python

    def is_valid_python(self):
        return (self.version_info[:2] >= (2, 5))

    def check_valid_python(self):
        if not self.is_valid_python():
            err_exit('Python >= 2.5 required')


class Process(object):

    def __init__(self, env=None):
        self.env = env

    def popen(self, cmd):
        """Execute an external command and return (rc, output).
        """
        process = Popen(cmd, shell=True, stdout=PIPE, env=self.env)
        stdoutdata, stderrdata = process.communicate()
        return process.returncode, stdoutdata


class Setuptools(object):

    def __init__(self):
        self.process = Process(env=self.get_env())
        self.python = Python()

    def get_env(self):
        # Make sure setuptools is found if mkrelease has
        # been installed with zc.buildout
        path = []
        for name in ('setuptools',):
            try:
                dist = pkg_resources.get_distribution(name)
            except pkg_resources.DistributionNotFound:
                continue
            path.append(dist.location)
        env = os.environ.copy()
        env['PYTHONPATH'] = ':'.join(path)
        return env

    def is_valid_package(self):
        return isfile('setup.py')

    def check_valid_package(self):
        if not self.is_valid_package():
            err_exit('No setup.py found in %s' % os.getcwd())

    def get_long_description(self):
        rc, long_description = self.process.popen(
            '"%s" setup.py --long-description' % self.python)
        if rc != 0:
            err_exit('Bad setup.py')
        if sys.version_info[0] >= 3:
            try:
                return long_description.decode('utf-8')
            except UnicodeDecodeError, e:
                err_exit('Error decoding long description: %s' % (e,))
        return long_description


class Docutils(object):

    def read_file(self, infile):
        """Read a reST file into a string.
        """
        try:
            with open(infile, 'rt') as file:
                return file.read()
        except UnicodeDecodeError, e:
            err_exit('Error decoding %s: %s' % (infile, e))
        except (IOError, OSError), e:
            err_exit('Error reading %s: %s' % (infile, e.strerror or e))

    def write_file(self, html, outfile):
        """Write an HTML string to a file.
        """
        try:
            with open(outfile, 'wt') as file:
                file.write(html)
        except (IOError, OSError), e:
            err_exit('Error writing %s: %s' % (outfile, e.strerror or e))

    def convert_string(self, rest):
        """Convert a reST string to an HTML string.
        """
        try:
            html = publish_string(rest, writer_name='html')
        except SystemExit, e:
            err_exit('HTML conversion failed with error: %s' % e.code)
        else:
            if sys.version_info[0] >= 3:
                return html.decode('utf-8')
            return html

    def strip_xml_header(self, html):
        """Strip any <?xml version="1.0" encoding="utf-8" ?> header.
        """
        if html.startswith('<?xml '):
            return html.split('\n', 1)[1]
        return html

    def apply_styles(self, html, styles):
        """Insert style information into the HTML string.
        """
        index = html.find('</head>')
        if index >= 0:
            return ''.join((html[:index], styles, html[index:]))
        return html

    def publish_string(self, rest, outfile, styles=''):
        """Render a reST string as HTML.
        """
        html = self.convert_string(rest)
        html = self.strip_xml_header(html)
        html = self.apply_styles(html, styles)
        self.write_file(html, outfile)
        return outfile

    def publish_file(self, infile, outfile, styles=''):
        """Render a reST file as HTML.
        """
        rest = self.read_file(infile)
        return self.publish_string(rest, outfile, styles)


class errors2warnings(object):
    """Turn ConfigParser.Errors into warnings."""

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        if isinstance(value, ConfigParser.Error):
            warn(str(value))
            return True


class Defaults(object):

    def __init__(self):
        """Read the config file.
        """
        filename = expanduser('~/.viewdoc')
        if not isfile(filename):
            self.write_default_config(filename)

        parser = ConfigParser.ConfigParser()
        with errors2warnings():
            parser.read(filename)

        def get(section, key, default=None):
            if parser.has_option(section, key):
                with errors2warnings():
                    return parser.get(section, key, raw=True)
            return default

        def getitems(section, default=None):
            if parser.has_section(section):
                with errors2warnings():
                    return parser.items(section, raw=True)
            return default

        self.known_styles = {}
        for key, value in getitems('styles', []):
            self.known_styles[key] = value.strip()+'\n'
        self.known_styles.setdefault('pypi', PYPI)

        self.default_style = get('viewdoc', 'style', 'pypi').strip()
        if self.default_style not in self.known_styles:
            self.default_style = 'pypi'

        self.styles = self.known_styles.get(self.default_style, '')

    def write_default_config(self, filename):
        """Write the default config file.
        """
        try:
            with open(filename, 'wt') as file:
                file.write(DEFAULT_CONFIG)
        except (IOError, OSError), e:
            print >>sys.stderr, 'Error writing %s: %s' % (filename, e.strerror or e)


class DocumentationViewer(object):

    def __init__(self, args):
        """Set defaults.
        """
        self.defaults = Defaults()
        self.python = Python()
        self.setuptools = Setuptools()
        self.docutils = Docutils()
        self.styles = self.defaults.styles
        self.args = args

    def parse_options(self, args):
        """Parse command line options.
        """
        style_names = tuple(self.defaults.known_styles)
        style_opts = tuple('--'+x for x in style_names)

        try:
            options, args = getopt.gnu_getopt(args, 'hls:v',
                ('help', 'style=', 'version', 'list-styles') + style_names)
        except getopt.GetoptError, e:
            err_exit('viewdoc: %s\n%s' % (e.msg, USAGE))

        for name, value in options:
            if name in ('-s', '--style'):
                self.styles = self.defaults.known_styles.get(value, '')
            elif name in style_opts:
                self.styles = self.defaults.known_styles.get(name[2:], '')
            elif name in ('-l', '--list-styles'):
                self.list_styles()
            elif name in ('-h', '--help'):
                msg_exit(HELP)
            elif name in ('-v', '--version'):
                msg_exit(VERSION)

        if len(args) > 1:
            err_exit('viewdoc: too many arguments\n%s' % USAGE)
        return args

    def list_styles(self):
        """Print available styles and exit.
        """
        for style in sorted(self.defaults.known_styles):
            if style == self.defaults.default_style:
                print style, '(default)'
            else:
                print style
        sys.exit(0)

    def render_file(self, filename):
        """Convert a reST file to HTML.
        """
        dirname, basename = split(filename)
        with changedir(dirname):
            infile = abspath(basename)
            outfile = abspath('.%s.html' % basename)
            self.docutils.publish_file(infile, outfile, self.styles)
            return outfile

    def render_long_description(self, dirname):
        """Convert a package's long description to HTML.
        """
        with changedir(dirname):
            self.setuptools.check_valid_package()
            long_description = self.setuptools.get_long_description()
            outfile = abspath('.long-description.html')
            self.docutils.publish_string(long_description, outfile, self.styles)
            return outfile

    def run(self):
        """Render and display Python package documentation.
        """
        self.python.check_valid_python()

        args = self.parse_options(self.args)
        if args:
            arg = args[0]
        else:
            arg = os.curdir
        if arg:
            arg = expanduser(arg)

        if isfile(arg):
            outfile = self.render_file(arg)
        elif isdir(arg):
            outfile = self.render_long_description(arg)
        else:
            err_exit('No such file or directory: %s' % arg)

        webbrowser.open('file://%s' % outfile)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    try:
        DocumentationViewer(args).run()
    except SystemExit, e:
        return e.code
    return 0


if __name__ == '__main__':
    sys.exit(main())

