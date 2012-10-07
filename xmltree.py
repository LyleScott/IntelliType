"""
Lyle Scott, III
lyle@digitalfoo.net
http://digitalfoo.net
"""

import hashlib
import os
import string

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

    token_subs = [('<', '__LESS_THAN__'),
                  ('>', '__GREATER_THAN__'),
                  ('&', '__AMPERSAND__'),
                  ('\'', '__SINGLE_QUOTE__'),
                  ('"', '__DOUBLE_QUOTE__'),
                  ('*', '__ASTERISK__'),
                  ('=', '__EQUALS__'),]
    

    def __init__(self, xml=None):
        """Initialization."""
        if xml:
            self.root = etree.fromstring(xml)
        else:
            self.root = etree.Element('querytree')
            
        self.tree = etree.ElementTree(self.root)
        self.invalid_char_map_fh = None

    def __repr__(self):
        """String representation."""
        return self.getXml(pretty_print=True)
    
    def __del__(self):
        """Destructor."""
        if self.invalid_char_map_fh:
            self.invalid_char_map_fh.close()
    
    def get_xml(self, pretty_print=True):
        """Return the XML of the entire XML Tree."""
        return etree.tostring(self.root, pretty_print=pretty_print)
    
    def generate_tokens_xpath(self, tokens):
        """Return the XPath representation for a list of tokens."""
        if not isinstance(tokens, list):
            tokens = (tokens,)
        return '//%s' % '/'.join(tokens)

    def tokenize(self, query):
        """Split a query up into a list of tokens."""
        if not query:
            return []
        
        if isinstance(query, list):
            query = ' '.join(query)

        query = query.lower()
        for search, replace in self.token_subs:
            query = query.replace(search, replace)
            
        for search in [token[1] for token in self.token_subs]:
            query = query.replace(search.lower(), search)
        
        query = query.split()
        
        return query

    def untokenize(self, query):
        """Join a query token list to make a string."""
        if isinstance(query, list):
            query = ' '.join(query)
        elif query.startswith('/querytree/'):
            query = query[len('/querytree/'):].replace('/', ' ')

        for replace, search in self.token_subs:
            query = query.replace(search, replace)

        return query

    def _get_invalid_character_map(self):
        """Get the file handle to the invalid character map CSV file if it
        isn't already available.
        """
        if not self.invalid_char_map_fh:
            filename = 'invalid_character_map.csv'
            if not os.path.exists(filename):
                mode = 'wb+'
            else:
                mode = 'rb+'
                
            self.invalid_char_map_fh = open(filename, mode)
        
        return self.invalid_char_map_fh

    def sanitize_xml(self, query):
        """Make a substitution for invalid characters."""
        valid_characters = ' %s' % string.ascii_letters
        self._get_invalid_character_map()
        
        # Replace the characters that are already known.
        for row in self.invalid_char_map_fh:
            if not row.strip():
                continue
            original, translation = row.split('|$|')
            query = query.replace(original, translation)
        
        # Add / translate any new illegal characters that are found.
        new_invalid_characters = []
        for character in query:
            if character not in valid_characters:
                md5 = hashlib.md5(character).hexdigest()
                shash = '__%s__' % md5
                query = query.replace(character, shash)
                new_invalid_characters.append('%s|$|%s\n' % (character, shash,))

        self.invalid_char_map_fh.writelines(new_invalid_characters)
        
        return query

    def unsanitize_xml(self, query):
        """ """
        self._get_invalid_character_map()
        for row in self.invalid_char_map_fh:
            if not row:
                continue
            translation, original = row.split('|$|')
            print '%s --> %s' % (translation, original,)
            query = query.replace(translation, original)
                
        return query
    
    def insert_query(self, root, query):
        """Insert a query into the tree."""
        query = self.sanitize_xml(query)
        tokens = self.tokenize(query)
        
        xpath = self.generate_tokens_xpath(tokens)
        if root.xpath(xpath):
            return
        
        prevtoken = root
        for i in range(len(tokens)):   
            subtokens = tokens[:i+1]
            subtokens_xpath = self.generate_tokens_xpath(subtokens)
            
            existing_path = root.xpath(subtokens_xpath)
            if not existing_path:
                prevtoken = etree.SubElement(prevtoken, tokens[i])
            else:
                prevtoken = existing_path[0]
                
        return prevtoken 
                
    def get_query_parts(self, query):
        """Try to split a query up into complete nodes and an incomplete token.
        If the user is starting a new token, return the entire string as nodes
        and make the token a blank string.
        """
        blank_at_end = query and query[-1] == ' '
        tokens = self.tokenize(query)
        if blank_at_end:
            node = ' '.join(tokens)
            node = self.untokenize(node)
            token = ''
        else:
            node = ' '.join(tokens[:-1])
            node = self.untokenize(node)
            if tokens:
                token = tokens[-1]
            else:
                token = ''

        return (node, token,)

    def get_autocompletes(self, query, token=None, mark=False, n_results=None,
                          next_token_only=False):
        """Try to find the exact node for a given query.
        
        query           -- a query to find in the XML tree
        token           -- a token to filter out would-be autocompletes
        next_token_only -- autocomplete the next token only instead of the
                           entire query
        """
        
        # argument sanity check
        if n_results is not None:
            try:
                n_results = int(n_results)
            except ValueError as e:
                print 'n_results is not an integer: %s' % e
                return []
        
        query = self.sanitize_xml(query)
        tokens = self.tokenize(query)
        xpath = self.generate_tokens_xpath(tokens)
        ret = []

        try:
            node = self.root.xpath(xpath)
        except etree.XPathEvalError:
            # The XPath to the node was not found.
            return []
        
        # Empty tree. 
        if not node:
            return []

        # Since a node was found, loop over each child to collect a proper
        # autocompletes.
        for child in node[0].getchildren():
            
            # The query does not autocomplete this token.
            if token and not child.tag.startswith(token):
                continue

            if next_token_only is True:    
                tag = self.untokenize(child.tag)
                if mark:
                    tag = '__MARK_START__%s__MARK_END__%s' % (tag[:len(token)], tag[len(token):])
                ret.append(tag)
            else:
                existing_queries = self.get_children_queries(child, include_self=True)
    
                if mark:
                    # Mark the substring of the query that is known.
                    for existing_query in existing_queries:
                        existing_query = '__MARK_START__%s' % existing_query
                        if token:
                            token = self.untokenize(token)
                            q = '%s %s' % (query, token,)
                        else:
                            q = query
                        existing_query = self.unsanitize_xml(existing_query)
                        print 'EXISTINGQ', existing_query
                        existing_query = existing_query.replace(q, q+'__MARK_END__')
                        
                        ret.append(existing_query)
                else:        
                    ret.extend(existing_queries)
                    
                if n_results:
                    if len(ret) > n_results:
                        ret = ret[:n_results]
                        break
                    elif len(ret) == n_results:
                        break
                
        return ret
                
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
            return paths

        for child in children:
            self.get_leaf_paths(child, paths)

        return paths       
    
    def get_children_queries(self, root=None, include_self=False):
        """Get a list of untokenized leafs below a node."""
        if root is None:
            root = self.root
        paths = []
        
        if include_self:
            paths.append(root)    
            
        paths.extend(self.get_leaf_paths(root))
        if paths:
            paths = [self.unsanitize_xml(self.untokenize(path))
                     for path in self.get_leaf_paths(root)]
    
        return paths or []
