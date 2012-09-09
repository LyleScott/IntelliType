"""
Lyle Scott, III
lyle@digitalfoo.net
http://digitalfoo.net
"""

import unittest

from xmltree import XMLTree
from lxml import etree


class XMLTreeTest(unittest.TestCase):
    """Test the functionality of the XMLTree object."""

    def setUp(self):
        """Stuff to do in test initialization."""
        
        self.queries = ( 
            'SELECT * FROM entityvals',
            'SELECT * FROM entityrelations WHERE id=1',
            'SELECT * FROM entities',)

    def assert_equals(self, v1, v2):
        try:
            assert v1 == v2
        except AssertionError:
            print '%s != %s' % (v1, v2,)
            raise

    def test_tokenize(self):
        """Tokenize a string to a list."""
        xmltree = XMLTree()

        v1 = xmltree.tokenize(self.queries[0])
        v2 = ['select', '__ASTERISK__', 'from', 'entityvals',]
        self.assert_equals(v1, v2)

        v1 = xmltree.tokenize(self.queries[1])
        v2 = ['select', '__ASTERISK__', 'from', 'entityrelations', 'where', 'id__EQUALS__1',]
        self.assert_equals(v1, v2)

        v1 = xmltree.tokenize(self.queries[2])
        v2 = ['select', '__ASTERISK__', 'from', 'entities',]
        self.assert_equals(v1, v2)

    def test_get_xpath(self):
        """ """
        xmltree = XMLTree()

        tokens = xmltree.tokenize(self.queries[0])
        v1 = xmltree._get_xpath(tokens) 
        v2 = '//select/__ASTERISK__/from/entityvals'
        self.assert_equals(v1, v2)

        tokens = xmltree.tokenize(self.queries[1])
        v1 = xmltree._get_xpath(tokens) 
        v2 = '//select/__ASTERISK__/from/entityrelations/where/id__EQUALS__1'
        self.assert_equals(v1, v2)

        tokens = xmltree.tokenize(self.queries[2])
        v1 = xmltree._get_xpath(tokens) 
        v2 = '//select/__ASTERISK__/from/entities'
        self.assert_equals(v1, v2)

    def test_insert_query(self):
        """Verify that queries get parsed to the correct XML."""
        xmltree = XMLTree()

        xmltree.insert_query(xmltree.root, self.queries[0])
        v1 = etree.tostring(xmltree.root)
        v2 = '<querytree><select><__ASTERISK__><from><entityvals/></from></__ASTERISK__></select></querytree>'
        self.assert_equals(v1, v2)

        xmltree.insert_query(xmltree.root, self.queries[1])
        v1 = etree.tostring(xmltree.root)
        v2 = '<querytree><select><__ASTERISK__><from><entityvals/><entityrelations><where><id__EQUALS__1/></where></entityrelations></from></__ASTERISK__></select></querytree>'
        self.assert_equals(v1, v2)
        
        xmltree.insert_query(xmltree.root, self.queries[2])
        v1 = etree.tostring(xmltree.root)
        v2 = '<querytree><select><__ASTERISK__><from><entityvals/><entityrelations><where><id__EQUALS__1/></where></entityrelations><entities/></from></__ASTERISK__></select></querytree>'
        self.assert_equals(v1, v2)

    def test_get_query_parts(self):
        """Verify a query can be split up into a node and an incomplete token.
        """
        xmltree = XMLTree()

        v1 = xmltree.get_query_parts('select * from entities')
        v2 = ('select * from', 'entities')
        self.assert_equals(v1, v2)
        
        # Test blank trailing space. Technically it is a start of a new token
        # which is thus blank.
        v1 = xmltree.get_query_parts('select * from entities ')
        v2 = ('select * from entities', '')
        self.assert_equals(v1, v2)

    def test_get_autocompletes(self):
        """Verify that a query can be correctly found in a xmltree object."""
        xmltree = XMLTree()

        v1 = xmltree.get_autocompletes('doesnotexist')
        v2 = []
        self.assert_equals(v1, v2)

        v1 = xmltree.get_autocompletes('//doesnotexist')
        v2 = []
        self.assert_equals(v1, v2)

        for query in self.queries:
            xmltree.insert_query(xmltree.root, query)

        v1 = xmltree.get_autocompletes('//doesnotexist')
        v2 = []
        self.assert_equals(v1, v2)

        query = 'select * doesnotexist'
        v1 = xmltree.get_autocompletes(query)
        v2 = []
        self.assert_equals(v1, v2)

        query = 'select * from'
        v1 = xmltree.get_autocompletes(query)
        v2 = ['entityvals', 'entityrelations', 'entities',]
        self.assert_equals(v1, v2)

    def test_get_leaf_nodes(self):
        """Verify leaf nodes are collected properly."""
        xmltree = XMLTree()
        for query in self.queries:
            xmltree.insert_query(xmltree.root, query)

        v1 = xmltree.get_leaf_nodes(xmltree.root)
        v1 = [node.tag for node in v1]
        v2 = [etree.Element('entityvals'),
              etree.Element('id__EQUALS__1'),
              etree.Element('entities'),]
        v2 = [node.tag for node in v2]
        self.assert_equals(v1, v2)

    def test_get_leaf_paths(self):
        """Verify leaf node paths are collected properly."""
        xmltree = XMLTree()
        for query in self.queries:
            xmltree.insert_query(xmltree.root, query)

        v1 = xmltree.get_leaf_paths(xmltree.root)
        v2 = ['/querytree/select/__ASTERISK__/from/entityvals',
              '/querytree/select/__ASTERISK__/from/entityrelations/where/id__EQUALS__1',
              '/querytree/select/__ASTERISK__/from/entities',]
        self.assert_equals(v1, v2)

        
if __name__ == '__main__':
    unittest.main()

