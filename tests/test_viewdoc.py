import unittest


class ViewdocTests(unittest.TestCase):

    def test_create(self):
        from jarn.viewdoc.viewdoc import DocumentationViewer
        DocumentationViewer([])

