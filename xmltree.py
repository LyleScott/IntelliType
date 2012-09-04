from lxml import etree


class XMLTree(object):
    """A class for storing, retrieving, and modifying an XML representation of 
    queries.

    Example:
        select * from foo 
        select * from bar
        select * from foo where id=1
 
        SELECT
          |
          *
          |
        FROM
          |
      __________
     foo       bar
      |
    where
      |
     id=1

    """

    def __init__(self):
        """Initialization."""
        self.root = etree.Element('querytree')
        self.tree = etree.ElementTree(self.root)

    def __repr__(self):
        """String representation."""
        return etree.tostring(self.root, pretty_print=1)

    def tokenize(self, query):
        """Split a query up into tokens."""
        query = query.replace('*', '__ALL__')
        query = query.split()

        return query

    def _get_xpath(self, tokens):
        """Return the XPath representation for a list of tokens."""
        return '//%s' % '/'.join(tokens)

    def insert_query(self, root, query):
        """Insert a query into the tree."""
        tokens = self.tokenize(query)
        prevtoken = root
        for i in range(len(tokens)):   
            subtokens = tokens[:i+1]
            subtokens_xpath = self._get_xpath(subtokens)
            existing_path = root.xpath(subtokens_xpath)
            if not existing_path:
                prevtoken = etree.SubElement(prevtoken, tokens[i])
            else:
                prevtoken = existing_path[0]

    def find_query(self, query):
        """Try to find the exact node for a given query."""
        tokens = self.tokenize(query)
        xpath = self._get_xpath(tokens)

        try:
            node = self.root.xpath(xpath)
        except etree.XPathEvalError:
            return []

        if node:
            if len(node) != 1:
                print 'ERROR'

            ret = []
            children = node[0].getchildren()

            for child in children:
                ret.append(child.tag)

            return ret

        return []
                
    def get_query_parts(self, query):
        """Try to split a query up into complete nodes and an incomplete token.
        If the user is starting a new token, return the entire string as nodes
        and make the token a blank string.
        """
        blank_at_end = query[-1] == ' '
        query = query.split()
        if blank_at_end:
            nodes = query
            token = ''
        else:
            nodes = query[:-1]
            token = query[-1]

        return (nodes, token,)

    def get_leaf_nodes(self, node, leaves=None):
        """Return all the leaf nodes in the tree."""
        if leaves is None:
            leaves = []

        children = node.getchildren()

        if not children:
            leaves.append(node)
            return

        for child in children:
            self.get_leaf_nodes(child, leaves)

        return leaves

    def get_leaf_paths(self, node, paths=None):
        """Return the paths of all leaf nodes."""
        if paths is None:
            paths = []

        children = node.getchildren()

        if not children:
            paths.append(self.tree.getpath(node))
            return

        for child in children:
            self.get_leaf_paths(child, paths)

        return paths


if __name__ == '__main__':
    xmltree = XMLTree()
    xmltree.insert_query(xmltree.root, 'select * from derp')
    xmltree.insert_query(xmltree.root, 'select * from yeah')

    print xmltree.get_leaf_nodes(xmltree.root)
    print xmltree.get_leaf_paths(xmltree.root)
