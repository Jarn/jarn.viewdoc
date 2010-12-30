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

from os.path import abspath, expanduser, dirname, basename
from os.path import split, join, isdir, isfile

from docutils.core import publish_string

version = "jarn.viewdoc %s" % __version__
usage = "Try 'viewdoc --help' for more information."
help = """\
Usage: viewdoc [options] [rst-file|egg-dir]

Documentation viewer

Options:
  -h, --help          Print this help message and exit.
  -v, --version       Print the version string and exit.

  rst-file            reST file to view.
  egg-dir             Package whose long description to view.
                      Defaults to the current working directory.
"""

styles = """\
<link rel="stylesheet" href="http://www.python.org/styles/styles.css" type="text/css"/>
<style type="text/css">
body { margin-left: 6em; margin-right: 6em; font-size: 95%; }
a { text-decoration: none; color: #0000aa; border-bottom: 1px dashed #cccccc; }
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


class DocumentationViewer(object):

    def __init__(self, args):
        """Set defaults.
        """
        self.python = sys.executable
        self.styles = styles
        self.args = args

    def parse_options(self, args):
        """Parse command line options.
        """
        try:
            options, args = getopt.gnu_getopt(args, 'hv', ('help', 'version'))
        except getopt.GetoptError, e:
            err_exit('viewdoc: %s\n%s' % (e.msg, usage))

        for name, value in options:
            if name in ('-v', '--version'):
                msg_exit(version)
            elif name in ('-h', '--help'):
                msg_exit(help)

        return args

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

    def rest_to_html(self, rest):
        """Run docutils and return an HTML string.
        """
        try:
            return publish_string(rest, writer_name='html')
        except SystemExit, e:
            err_exit('HTML conversion failed with error: %s' % e.code)

    def apply_styles(self, html):
        """Insert style information into the HTML string.
        """
        index = html.index('</head>')
        if index < 0:
            return html
        return ''.join((html[:index], self.styles, html[index:]))

    def render(self, infile, outfile):
        """Render a reST file as HTML.
        """
        rest = self.read_file(infile)
        html = self.rest_to_html(rest)
        html = self.apply_styles(html)
        self.write_file(html, outfile)

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
            self.render(infile, outfile)
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
                err_exit('No setup.py found in %s' % os.getcwd())

            tempdir = abspath(tempfile.mkdtemp(prefix='viewdoc-'))
            try:
                infile = join(tempdir, 'long-description.rst')
                outfile = abspath('.long-description.html')
                rc = os.system('"%s" setup.py --long-description > "%s"' % (self.python, infile))
                if rc != 0:
                    err_exit('HTML conversion failed with error: %s' % rc)
                self.render(infile, outfile)
                return outfile
            finally:
                shutil.rmtree(tempdir)
        finally:
            os.chdir(saved)

    def run(self):
        """Render and display Python package documentation.
        """
        args = self.parse_options(self.args)
        if args:
            arg = args.pop(0)
        else:
            arg = os.curdir
        if args:
            err_exit('viewdoc: too many arguments\n%s' % usage)

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

