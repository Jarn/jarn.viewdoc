from __future__ import absolute_import
from __future__ import print_function

import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    pass

import pkg_resources
__version__ = pkg_resources.get_distribution('jarn.viewdoc').version

import sys
import os
import getopt
import shutil
import webbrowser

from os.path import abspath, expanduser, split, isdir, isfile, exists
from functools import partial
from subprocess import Popen, PIPE
from docutils.core import publish_string

from .configparser import ConfigParser
from .colors import red

VERSION = "jarn.viewdoc %s" % __version__
USAGE = "Try 'viewdoc --help' for more information"

HELP = """\
Usage: viewdoc [options] [rst-file|egg-dir]

Python documentation viewer

Options:
  -s style, --style=style, or --style
                        Select the custom style added to the HTML output.

  -b browser, --browser=browser
                        Select the browser used for display.

  -c config-file, --config-file=config-file
                        Use config-file instead of the default ~/.viewdoc.

  -l, --list-styles     List available styles and exit.
  -h, --help            Print this help message and exit.
  -v, --version         Print the version string and exit.

  --no-color            Disable output colors.
  --no-browser          Print HTML to stdout.

Arguments:
  rst-file              reST file to view.
  egg-dir               Package whose long description to view. Defaults to
                        the current working directory.
"""

PLAIN = """
    <style type="text/css">
    body { margin-left: 20%; margin-right: 20%; }
    </style>
"""

CLASSIC = """
    <link rel="stylesheet" href="http://pypi.python.org/static/styles/styles.css" type="text/css" />
    <style type="text/css">
    body { margin-left: 20%; margin-right: 20%; font-size: 95%; }
    a:link { text-decoration: none; color: #0000aa; }
    a:visited { text-decoration: none; color: #551a8b; }
    a.reference { border-bottom: 1px dashed #cccccc; }
    </style>
"""

PYPI = """
    <link rel="stylesheet" href="http://pypi.python.org/static/styles/styles.css" type="text/css" />
    <link rel="stylesheet" media="screen" href="http://pypi.python.org/static/css/pygments.css" type="text/css" />
    <link rel="stylesheet" href="http://pypi.python.org/static/css/pypi.css" type="text/css" />
    <link rel="stylesheet" media="screen" href="http://pypi.python.org/static/css/pypi-screen.css" type="text/css" />
    <style type="text/css">
    body { margin-left: 20%; margin-right: 20%; font-size: 95%; }
    a:link { text-decoration: none; color: #0000aa; }
    a:visited { text-decoration: none; color: #551a8b; }
    a.reference { border-bottom: 1px dashed #cccccc; }
    pre.literal-block { background-color: #f0f0f0; }
    </style>
"""

SMALL = """
    <link rel="stylesheet" href="http://pypi.python.org/static/styles/styles.css" type="text/css" />
    <link rel="stylesheet" media="screen" href="http://pypi.python.org/static/css/pygments.css" type="text/css" />
    <link rel="stylesheet" href="http://pypi.python.org/static/css/pypi.css" type="text/css" />
    <link rel="stylesheet" media="screen" href="http://pypi.python.org/static/css/pypi-screen.css" type="text/css" />
    <style type="text/css">
    body { margin-left: 20%; margin-right: 20%; font-size: 90%; }
    a:link { text-decoration: none; color: #0000aa; }
    a:visited { text-decoration: none; color: #551a8b; }
    a.reference { border-bottom: 1px dashed #cccccc; }
    pre.literal-block { background-color: #f0f0f0; }
    </style>
"""

SANS = """
    <style type="text/css">
    body {
        font-family: Helvetica,Arial,sans-serif;
        line-height: 1.4;
        margin-left: 20%;
        margin-right: 20%;
    }
    pre.literal-block {
        background-color: #f9f9f9;
        border: 1px solid #d3d3d3;
        margin-left: 0;
        padding: 1em;
    }
    a {
        text-decoration: none;
        color: #0070d0;
    }
    a:hover, a:focus {
        text-decoration: underline;
    }
    </style>
"""

WAREHOUSE = """
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,400italic,600,600italic,700,700italic|Source+Code+Pro:500">
    <style type="text/css">
    body {
        font-family: Source Sans Pro,Helvetica,Arial,sans-serif;
        font-size: 17px;
        font-weight: 300;
        line-height: 1.4;
        color: #464646;
        background-color: #fdfdfd;
    }
    code, kbd, pre, samp, tt, pre.code {
        font-family: Source Code Pro,monospace;
        font-size: 85%;
        color: #6c6c6c;
        background-color: #f9f9f9;
        border: 1px solid #d3d3d3;
        padding: 0 2px 1px;
    }
    a {
        color: #006dad;
        text-decoration: none;
    }
    a:hover {
        color: #004d7a;
        text-decoration: underline;
    }
    a:focus {
        text-decoration: underline;
    }
    body {
        margin-left: 20%;
        margin-right: 20%;
    }
    pre.literal-block {
        margin-left: 0;
        padding: 1em;
    }
    dl.docutils dt {
        margin-top: 1em;
    }
    dl.docutils dd {
        margin-bottom: 1em;
    }
    </style>
"""

CONFIG_VERSION = '2.4'

DEFAULT_CONFIG = """\
[viewdoc]
version = %(CONFIG_VERSION)s
style = sans
browser = default

[styles]
plain =%(PLAIN)s
sans =%(SANS)s
pypi =%(WAREHOUSE)s
""" % locals()


# Open files as UTF-8
if sys.version_info[0] >= 3:
    open = partial(open, encoding='utf-8')


def msg_exit(msg, rc=0):
    """Print msg to stdout and exit with rc.
    """
    print(msg)
    sys.exit(rc)


def err_exit(msg, rc=1):
    """Print msg to stderr and exit with rc.
    """
    if '\033[' not in msg:
        lines = msg.split('\n')
        lines[0] = red(lines[0])
        msg = '\n'.join(lines)
    print(msg, file=sys.stderr)
    sys.exit(rc)


def warn(msg):
    """Print warning msg to stderr.
    """
    print('WARNING:', msg, file=sys.stderr)


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
        return (self.version_info[:2] >= (2, 7))

    def check_valid_python(self):
        if not self.is_valid_python():
            err_exit('viewdoc: Python >= 2.7 required')


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
        # Make sure dependencies are found if viewdoc has
        # been installed with zc.buildout
        env = os.environ.copy()
        env['PYTHONPATH'] = ':'.join(sys.path)
        return env

    def is_valid_package(self):
        return isfile('setup.py') or isfile('setup.cfg')

    def check_valid_package(self):
        if not self.is_valid_package():
            err_exit('viewdoc: No setup.py in %s' % os.getcwd())

    def get_long_description(self):
        parser = ConfigParser(warn)
        parser.read('setup.cfg')
        if parser.warnings:
            err_exit('viewdoc: Bad setup in %s' % os.getcwd())

        rc, long_description = self._run_setup_py(['--long-description'])

        if rc != 0:
            err_exit('viewdoc: Bad setup in %s' % os.getcwd())
        if sys.version_info[0] >= 3:
            try:
                return long_description.decode('utf-8')
            except UnicodeDecodeError as e:
                err_exit('viewdoc: Error reading long description: %s' % (e,))
        return long_description

    def _run_setup_py(self, args):
        """Run setup.py with monkey-patched setuptools.

        'args' is the list of arguments that should be passed to
        setup.py.
        """
        python = self.python
        run_setup = 'from jarn.viewdoc import setup; setup.run(%(args)r)'

        setup_py = '-c"%s"' % (run_setup % locals())

        rc, stdoutdata = self.process.popen(
            '"%(python)s" %(setup_py)s' % locals())

        return rc, stdoutdata


class Docutils(object):

    def read_file(self, infile):
        """Read a reST file into a string.
        """
        try:
            with open(infile, 'rt') as file:
                return file.read()
        except UnicodeDecodeError as e:
            err_exit('viewdoc: Error reading %s: %s' % (infile, e))
        except (IOError, OSError) as e:
            err_exit('viewdoc: Error reading %s: %s' % (infile, e.strerror or e))

    def write_file(self, html, outfile):
        """Write an HTML string to a file.
        """
        try:
            with open(outfile, 'wt') as file:
                file.write(html)
        except (IOError, OSError) as e:
            err_exit('viewdoc: Error writing %s: %s' % (outfile, e.strerror or e))

    def convert_string(self, rest):
        """Convert a reST string to an HTML string.
        """
        try:
            html = publish_string(rest, writer_name='html')
        except SystemExit as e:
            err_exit('viewdoc: HTML conversion failed with error: %s' % e.code)
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


class Defaults(object):

    def __init__(self, config_file):
        """Read the config file.
        """
        self.filename = config_file

        parser = ConfigParser(warn)
        parser.read(self.filename)

        self.warnings = parser.warnings

        self.version = parser.getstring('viewdoc', 'version', '') or '1.8'
        self.browser = parser.getstring('viewdoc', 'browser', '') or 'default'

        self.known_styles = {}
        for key, value in parser.items('styles', []):
            self.known_styles[key] = value.strip()

        self.default_style = parser.getstring('viewdoc', 'style', '')
        self.styles = self.known_styles.get(self.default_style, '')

        if os.environ.get('JARN_RUN') == '1':
            if parser.warnings:
                err_exit('viewdoc: Bad configuration')

    def write(self):
        """Create the config file.
        """
        warn('Creating ' + self.filename)
        return self.write_default_config(self.filename)

    def upgrade(self):
        """Upgrade the config file.
        """
        warn('Upgrading ' + self.filename)
        if self.backup_config(self.filename):
            return self.write_default_config(self.filename)
        return False

    def backup_config(self, filename):
        """Backup the current config file.
        """
        backup_name = filename + '-' + self.version
        warn('Moving current configuration to ' + backup_name)
        try:
            shutil.copy2(filename, backup_name)
            return True
        except (IOError, OSError) as e:
            print('Error copying %s: %s' % (filename, e.strerror or e), file=sys.stderr)
            return False

    def write_default_config(self, filename):
        """Write the default config file.
        """
        try:
            with open(filename, 'wt') as file:
                file.write(DEFAULT_CONFIG)
            return True
        except (IOError, OSError) as e:
            print('Error writing %s: %s' % (filename, e.strerror or e), file=sys.stderr)
            return False


class DocumentationViewer(object):

    def __init__(self, args):
        """Initialize.
        """
        self.args = args

    def set_defaults(self, config_file):
        """Set defaults.
        """
        self.defaults = Defaults(config_file)
        self.python = Python()
        self.setuptools = Setuptools()
        self.docutils = Docutils()
        self.styles = self.defaults.styles
        self.browser = self.defaults.browser
        self.list = False
        self.no_browser = False

    def reset_defaults(self, config_file):
        """Reset defaults.
        """
        if not exists(config_file):
            err_exit('viewdoc: No such file: %(config_file)s' % locals())
        if not isfile(config_file):
            err_exit('viewdoc: Not a file: %(config_file)s' % locals())
        if not os.access(config_file, os.R_OK):
            err_exit('viewdoc: Cannot read: %(config_file)s' % locals())
        self.set_defaults(config_file)

    def write_defaults(self):
        """Create default config file and reload.
        """
        self.defaults.write()
        self.reset_defaults(self.defaults.filename)

    def upgrade_defaults(self):
        """Upgrade config file and reload.
        """
        self.defaults.upgrade()
        self.reset_defaults(self.defaults.filename)

    def parse_options(self, args, depth=0):
        """Parse command line options.
        """
        style_names = tuple(self.defaults.known_styles)
        style_opts = tuple('--'+x for x in style_names)

        try:
            options, remaining_args = getopt.gnu_getopt(args, 'b:c:hls:v',
                ('help', 'style=', 'version', 'list-styles', 'browser=',
                 'config-file=', 'no-color', 'no-browser') + style_names)
        except getopt.GetoptError as e:
            err_exit('viewdoc: %s\n%s' % (e.msg.capitalize(), USAGE))

        for name, value in options:
            if name in ('-s', '--style'):
                self.styles = self.defaults.known_styles.get(value, '')
            elif name in style_opts:
                self.styles = self.defaults.known_styles.get(name[2:], '')
            elif name in ('-b', '--browser'):
                self.browser = value
            elif name in ('-l', '--list-styles'):
                self.list = True
            elif name in ('-h', '--help'):
                msg_exit(HELP)
            elif name in ('-v', '--version'):
                msg_exit(VERSION)
            elif name in ('--no-color',):
                os.environ['JARN_NO_COLOR'] = '1'
            elif name in ('--no-browser',):
                self.no_browser = True
            elif name in ('-c', '--config-file') and depth == 0:
                self.reset_defaults(expanduser(value))
                return self.parse_options(args, depth+1)

        if len(remaining_args) > 1:
            err_exit('viewdoc: Too many arguments\n%s' % USAGE)

        if not isfile(self.defaults.filename) and depth == 0:
            self.write_defaults()
            return self.parse_options(args, depth+1)

        if self.defaults.version < CONFIG_VERSION and depth == 0:
            self.upgrade_defaults()
            return self.parse_options(args, depth+1)

        if self.list:
            self.list_styles()

        return remaining_args

    def list_styles(self):
        """Print available styles and exit.
        """
        known = sorted(self.defaults.known_styles)
        if not known:
            err_exit('viewdoc: No styles', 0)
        for style in known:
            if style == self.defaults.default_style:
                print(style, '(default)')
            else:
                print(style)
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

    def print_file(self, outfile):
        """Print the given HTML file to stdout.
        """
        try:
            with open(outfile, 'r') as f:
                print(f.read(), end='')
        except (IOError, OSError) as e:
            err_exit('viewdoc: Error reading %s: %s' % (outfile, e.strerror or e))

    def open_in_browser(self, outfile):
        """Open the given HTML file in a browser.
        """
        try:
            if self.browser == 'default':
                webbrowser.open('file://%s' % outfile)
            else:
                browser = webbrowser.get(self.browser)
                browser.open('file://%s' % outfile)
        except webbrowser.Error as e:
            err_exit('viewdoc: %s' % (str(e).capitalize(),))

    def get_env(self):
        os.environ['JARN_RUN'] = '1'

        for arg in self.args:
            if arg in ('--no-c', '--no-co', '--no-col', '--no-colo', '--no-color'):
                os.environ['JARN_NO_COLOR'] = '1'
                break

    def run(self):
        """Render and display Python package documentation.
        """
        self.get_env()
        self.set_defaults(expanduser('~/.viewdoc'))
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
            err_exit('viewdoc: No such file or directory: %s' % arg)

        if self.no_browser:
            self.print_file(outfile)
        else:
            self.open_in_browser(outfile)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    try:
        DocumentationViewer(args).run()
    except SystemExit as e:
        return e.code
    return 0


if __name__ == '__main__':
    sys.exit(main())

