import unittest

from jarn.viewdoc.viewdoc import DocumentationViewer

from jarn.viewdoc.testing import JailSetup
from jarn.viewdoc.testing import quiet


class GetOptionsTests(JailSetup):

    def test_defaults(self):
        self.mkfile('my.cfg', """\
[viewdoc]
""")
        dv = DocumentationViewer(['-c', 'my.cfg'])
        dv.set_defaults('my.cfg')
        dv.parse_options(dv.args)
        self.assertEqual(dv.defaults.version, '1.8')
        self.assertEqual(dv.defaults.browser, 'default')
        self.assertEqual(dv.defaults.known_styles, {})
        self.assertEqual(dv.defaults.default_style, '')
        self.assertEqual(dv.defaults.styles, '')
        self.assertEqual(dv.browser, 'default')
        self.assertEqual(dv.styles, '')

    @quiet
    def test_quiet(self):
        print('Should not be visible')

    def test_empty_defaults(self):
        self.mkfile('my.cfg', """\
[viewdoc]
version =
browser =
style =

[styles]
pypi =
""")
        dv = DocumentationViewer(['-c', 'my.cfg'])
        dv.set_defaults('my.cfg')
        dv.parse_options(dv.args)
        self.assertEqual(dv.defaults.version, '1.8')
        self.assertEqual(dv.defaults.browser, 'default')
        self.assertEqual(dv.defaults.known_styles, {'pypi': ''})
        self.assertEqual(dv.defaults.default_style, '')
        self.assertEqual(dv.defaults.styles, '')
        self.assertEqual(dv.browser, 'default')
        self.assertEqual(dv.styles, '')

    def test_read_defaults(self):
        self.mkfile('my.cfg', """\
[viewdoc]
version = 2.0
browser = safari
style = pypi

[styles]
pypi = <style></style>
""")
        dv = DocumentationViewer(['-c', 'my.cfg'])
        dv.set_defaults('my.cfg')
        dv.parse_options(dv.args)
        self.assertEqual(dv.defaults.version, '2.0')
        self.assertEqual(dv.defaults.browser, 'safari')
        self.assertEqual(dv.defaults.known_styles, {'pypi': '<style></style>'})
        self.assertEqual(dv.defaults.default_style, 'pypi')
        self.assertEqual(dv.defaults.styles, '<style></style>')
        self.assertEqual(dv.browser, 'safari')
        self.assertEqual(dv.styles, '<style></style>')

    def test_newline_in_defaults(self):
        self.mkfile('my.cfg', """\
[viewdoc]
version =
    2.0
browser =
    safari
style =
    pypi

[styles]
pypi =
    <style>
    </style>

plain =
""")
        dv = DocumentationViewer(['-c', 'my.cfg'])
        dv.set_defaults('my.cfg')
        dv.parse_options(dv.args)
        self.assertEqual(dv.defaults.version, '2.0')
        self.assertEqual(dv.defaults.browser, 'safari')
        self.assertEqual(dv.defaults.known_styles, {'pypi': '<style>\n</style>', 'plain': ''})
        self.assertEqual(dv.defaults.default_style, 'pypi')
        self.assertEqual(dv.defaults.styles, '<style>\n</style>')
        self.assertEqual(dv.browser, 'safari')
        self.assertEqual(dv.styles, '<style>\n</style>')

    def test_unknown_style(self):
        self.mkfile('my.cfg', """\
[viewdoc]
style = foo

[styles]
pypi = <style></style>
""")
        dv = DocumentationViewer(['-c', 'my.cfg'])
        dv.set_defaults('my.cfg')
        dv.parse_options(dv.args)
        self.assertEqual(dv.defaults.known_styles, {'pypi': '<style></style>'})
        self.assertEqual(dv.defaults.default_style, 'foo')
        self.assertEqual(dv.defaults.styles, '')
        self.assertEqual(dv.browser, 'default')
        self.assertEqual(dv.styles, '')

    def test_command_line(self):
        self.mkfile('my.cfg', """\
[viewdoc]
browser = safari
style = pypi

[styles]
pypi = <style>1</style>
small  = <style>2</style>
""")
        dv = DocumentationViewer(['-c', 'my.cfg', '-s', 'small', '-b', 'firefox'])
        dv.set_defaults('my.cfg')
        dv.parse_options(dv.args)
        self.assertEqual(dv.defaults.browser, 'safari')
        self.assertEqual(dv.defaults.known_styles, {'pypi': '<style>1</style>', 'small': '<style>2</style>'})
        self.assertEqual(dv.defaults.default_style, 'pypi')
        self.assertEqual(dv.defaults.styles, '<style>1</style>')
        self.assertEqual(dv.browser, 'firefox')
        self.assertEqual(dv.styles, '<style>2</style>')

