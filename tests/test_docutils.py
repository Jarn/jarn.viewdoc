import sys
import unittest


class DocutilsTests(unittest.TestCase):

    def test_publish_string(self):
        from docutils.core import publish_string

        s = publish_string('foo', writer_name='html')
        self.assertTrue(s.startswith(b'<?xml version="1.0" encoding="utf-8"'))

