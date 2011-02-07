import locale
locale.setlocale(locale.LC_ALL, '')

import pkg_resources
__version__ = pkg_resources.get_distribution('jarn.viewdoc').version

import sys
import os
import getopt
import tempfile
import shutil
import webbrowser
import ConfigParser

from os.path import abspath, expanduser, dirname, basename
from os.path import split, join, isdir, isfile

from docutils.core import publish_string

VERSION = "jarn.viewdoc %s" % __version__
USAGE = "Try 'viewdoc --help' for more information."

HELP = """\
Usage: viewdoc [options] [rst-file|egg-dir]

Documentation viewer

Options:
  -s style, --style=style
                      Select the style added to the HTML output.

  -h, --help          Print this help message and exit.
  -v, --version       Print the version string and exit.

  rst-file            reST file to view.
  egg-dir             Package whose long description to view.
                      Defaults to the current working directory.
"""

STYLES = """\
<link rel="stylesheet" href="http://www.python.org/styles/styles.css" type="text/css" />
<style type="text/css">
body { margin-left: 10em; margin-right: 10em; font-size: 95%; }
a { text-decoration: none; color: #0000aa; border-bottom: 1px dashed #cccccc; }
a:visited { text-decoration: none; color: #551a8b; border-bottom: 1px dashed #cccccc; }
</style>
"""

CONFIG = """\
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
    a:link { text-decoration: none; color: #0000aa; border-bottom: 1px dashed #cccccc; }
    a:visited { text-decoration: none; color: #551a8b; border-bottom: 1px dashed #cccccc; }
    </style>
"""


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


class Defaults(object):

    def __init__(self):
        """Read the config file.
        """
        filename = expanduser('~/.viewdoc')
        if not isfile(filename):
            self.write_default(filename)

        parser = ConfigParser.ConfigParser()
        parser.read(filename)

        def get(section, key, default=None):
            if parser.has_option(section, key):
                return parser.get(section, key)
            return default

        self.available_styles = {}
        if parser.has_section('styles'):
            for key, value in parser.items('styles'):
                self.available_styles[key] = value.strip()+'\n'

        self.default_style = get('viewdoc', 'style', 'pypi')
        self.available_styles.setdefault('pypi', STYLES)

        self.styles = self.available_styles.get(self.default_style, '')

    def write_default(self, filename):
        """Write the default config file.
        """
        try:
            f = open(filename, 'wt')
            try:
                f.write(CONFIG)
            finally:
                f.close()
        except (IOError, OSError), e:
            print >>sys.stderr, '%s: %s' % (e.strerror or e, filename)


class Docutils(object):

    def read_file(self, infile):
        """Read a reST file into a string.
        """
        try:
            f = open(infile, 'rt')
            try:
                return f.read()
            finally:
                f.close()
        except (IOError, OSError), e:
            err_exit('%s: %s' % (e.strerror or e, infile))

    def write_file(self, html, outfile):
        """Write an HTML string to a file.
        """
        try:
            f = open(outfile, 'wt')
            try:
                f.write(html)
            finally:
                f.close()
        except (IOError, OSError), e:
            err_exit('%s: %s' % (e.strerror or e, outfile))

    def publish_string(self, rest):
        """Convert a reST string to an HTML string.
        """
        try:
            return publish_string(rest, writer_name='html')
        except SystemExit, e:
            err_exit('HTML conversion failed with error: %s' % e.code)

    def apply_styles(self, html, styles):
        """Insert style information into the HTML string.
        """
        index = html.find('</head>')
        if index < 0:
            return html
        return ''.join((html[:index], styles, html[index:]))

    def run(self, infile, outfile, styles=''):
        """Render a reST file as HTML.
        """
        rest = self.read_file(infile)
        html = self.publish_string(rest)
        html = self.apply_styles(html, styles)
        self.write_file(html, outfile)


class DocumentationViewer(object):

    def __init__(self, args):
        """Set defaults.
        """
        self.defaults = Defaults()
        self.docutils = Docutils()
        self.styles = self.defaults.styles
        self.args = args

    def parse_options(self, args):
        """Parse command line options.
        """
        try:
            options, args = getopt.gnu_getopt(args, 'hs:v', ('help', 'style=', 'version'))
        except getopt.GetoptError, e:
            err_exit('viewdoc: %s\n%s' % (e.msg, USAGE))

        for name, value in options:
            if name in ('-s', '--style'):
                self.styles = self.defaults.available_styles.get(value, '')
            elif name in ('-v', '--version'):
                msg_exit(VERSION)
            elif name in ('-h', '--help'):
                msg_exit(HELP)

        if len(args) > 1:
            err_exit('viewdoc: too many arguments\n%s' % USAGE)
        return args

    def render_file(self, filename):
        """Convert a reST file to HTML.
        """
        saved = os.getcwd()
        dirname, basename = split(filename)
        if dirname:
            os.chdir(dirname)
        try:
            infile = abspath(basename)
            outfile = abspath('.%s.html' % basename)
            self.docutils.run(infile, outfile, self.styles)
            return outfile
        finally:
            os.chdir(saved)

    def render_long_description(self, dirname):
        """Convert a package's long description to HTML.
        """
        saved = os.getcwd()
        if dirname:
            os.chdir(dirname)
        try:
            if not isfile('setup.py'):
                err_exit('Not eggified (no setup.py found): %s' % os.getcwd())

            tempdir = abspath(tempfile.mkdtemp(prefix='viewdoc-'))
            try:
                infile = join(tempdir, 'long-description.rst')
                outfile = abspath('.long-description.html')
                rc = os.system('"%s" setup.py --long-description > "%s"' % (sys.executable, infile))
                if rc != 0:
                    err_exit('HTML conversion failed with error: %s' % rc)
                self.docutils.run(infile, outfile, self.styles)
                return outfile
            finally:
                shutil.rmtree(tempdir)
        finally:
            os.chdir(saved)

    def run(self):
        """Render and display Python package documentation.
        """
        if sys.version_info[:2] < (2, 4):
            err_exit('Python >= 2.4 required')

        args = self.parse_options(self.args)
        if args:
            arg = args[0]
        else:
            arg = os.curdir

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

