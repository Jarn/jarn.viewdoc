import sys
import unittest


class DocutilsTests(unittest.TestCase):

    def test_publish_string(self):
        from docutils.core import publish_string

        s = publish_string('foo', writer_name='html')
        if sys.version_info[0] >= 3:
            s = s.decode('utf-8')
        self.assertTrue(s.startswith('<?xml version="1.0" encoding="utf-8"'))

