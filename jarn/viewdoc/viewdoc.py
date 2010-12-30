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

from docutils.core import publish_file

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

    def run_rst2html(self, infile, outfile):
        """Run the docutils publisher.
        """
        try:
            publish_file(writer_name='html', source_path=infile, destination_path=outfile)
        except SystemExit, e:
            return e.code
        return 0

    def apply_styles(self, outfile):
        """Insert style information into the HTML file.
        """
        f = open(outfile, 'rt')
        lines = f.readlines() # XXX: Really?
        f.close()
        f = open(outfile, 'wt')
        done = False
        for line in lines:
            if not done and line.strip() == '</head>':
                f.write(self.styles)
                done = True
            f.write(line)
        f.close()

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
            rc = self.run_rst2html(infile, outfile)
            return rc, outfile
        finally:
            os.chdir(saved)

    def render_long_description(self, dirname):
        """Convert a package's long description to HTML.
        """
        saved = os.getcwd()
        os.chdir(dirname)
        try:
            if not isfile('setup.py'):
                err_exit('No setup.py found in %s' % os.getcwd())

            tempdir = abspath(tempfile.mkdtemp(prefix='viewdoc-'))
            try:
                infile = join(tempdir, 'tempfile.rst')
                outfile = abspath('.long-description.html')
                rc = os.system('"%s" setup.py --long-description > "%s"' % (self.python, infile))
                if rc == 0:
                    rc = self.run_rst2html(infile, outfile)
                return rc, outfile
            finally:
                shutil.rmtree(tempdir)
        finally:
            os.chdir(saved)

    def run(self):
        """Render and display package documentation.
        """
        args = self.parse_options(self.args)

        if args:
            arg = args.pop(0)
        else:
            arg = os.curdir

        if args:
            err_exit('viewdoc: too many arguments\n%s' % usage)

        if isfile(arg):
            rc, outfile = self.render_file(arg)
        elif isdir(arg):
            rc, outfile = self.render_long_description(arg)
        else:
            err_exit('No such file or directory: %s' % arg)
        if rc != 0:
            err_exit('HTML conversion failed with return code: %s' % rc, rc)

        self.apply_styles(outfile)
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

