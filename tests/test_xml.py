import unittest

import guesstype
from lxml import etree


class XMLTreeTest(unittest.TestCase):

    def setUp(self):
        """Stuff to do in test initialization."""
        
        self.queries = ( 
            'SELECT * FROM entityvals',
            'SELECT * FROM entityrelations',
            'SELECT * FROM entities',)

    def test_tokenize(self):
        """Tokenize a string to a list."""
        

    def test_insert_query(self):
        """Verify that queries get parsed to the correct XML."""
        xmltree = guesstype.XMLTree()
        
        xmltree.insert_query(xmltree.root, self.queries[0])
        assert etree.tostring(xmltree.root) == '<querytree><SELECT><__ALL__><FROM><entityvals/></FROM></__ALL__></SELECT></querytree>'
        
        xmltree.insert_query(xmltree.root, self.queries[1])
        assert etree.tostring(xmltree.root) == '<querytree><SELECT><__ALL__><FROM><entityvals/><entityrelations/></FROM></__ALL__></SELECT></querytree>'
        
        xmltree.insert_query(xmltree.root, self.queries[2])
        assert etree.tostring(xmltree.root) == '<querytree><SELECT><__ALL__><FROM><entityvals/><entityrelations/><entities/></FROM></__ALL__></SELECT></querytree>'

        
if __name__ == '__main__':
    unittest.main()

