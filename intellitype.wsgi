#!/usr/bin/env python
"""
Lyle Scott, III
lyle@digitalfoo.net
http://digitalfoo.net
"""

import json
import os
import re
import xmltree

from lxml import etree 
from urlparse import parse_qsl


XML_DIR = 'xmls'
RE_HOST = r'[^A-Za-z0-9\.]'

def getXmlFile(httphost, mode='r'):
    """Create a flat-file to store some XML."""
    if not os.path.exists(XML_DIR):
        os.mkdir(XML_DIR)
     
    httphost = re.sub(RE_HOST, '', httphost)
    path = os.path.join(XML_DIR, httphost + '.xml')
    
    if mode.startswith('r') and not os.path.exists(path):
        xmlfile = open(path, 'w')
        closeXmlFile(xmlfile)
    
    return open(path, mode)

def closeXmlFile(file):
    """Close a file handle."""
    file.close()
    
def saveXmlFile(xml, file):
    """Write some XML to file handle."""
    file.write(xml)
    
def cbGetSuggestionsHandler(userinput, httphost, mark=False, num_results=None):
    """Callback handler for get_suggestions."""
    xmlfile = getXmlFile(httphost)
    xml = xmlfile.read()
    xtree = xmltree.XMLTree(xml)
    nodes, token = xtree.get_query_parts(userinput)
    results = xtree.get_autocompletes(nodes, token)
    
    _results = []
    
    if mark:
        nodes = '__MARK_START__%s' % nodes
    
    for result in results:
        if mark:
            result = result.replace(token, '%s__MARK_END__' % token)
            
        _results.append('%s %s' % (nodes, result,))
        
        if len(_results) == num_results:
            break
        
    closeXmlFile(xmlfile)
    return 'get_suggestions({"results": %s})' % json.dumps(_results)   

def cbSubmitQueryHandler(userinput, httphost):
    """Callback handler for submit_query."""
    # Insert the query into the existing tree.
    xmlfile = getXmlFile(httphost)
    xml = xmlfile.read()
    xtree = xmltree.XMLTree(xml)
    xtree.insert_query(xtree.root, userinput)
    newxml = etree.tostring(xtree.root, pretty_print=True)
    closeXmlFile(xmlfile)
    
    # Save the new version of the tree.
    xmlfile = getXmlFile(httphost, mode='w')
    saveXmlFile(newxml, xmlfile)
    closeXmlFile(xmlfile)

    return ['submit_query({"success": true})',]

def cbGetExistingQueries(httphost):
    """Get all existing queries."""
    xmlfile = getXmlFile(httphost)
    xml = xmlfile.read()
    xtree = xmltree.XMLTree(xml)
    paths = xtree.get_existing_queries(xtree.root)
    closeXmlFile(xmlfile)

    return ['get_existing({"results": %s})' % json.dumps(paths),]


def application(environ, start_response):
    """Basically, fire off the callback handler."""
    headers = [('Content-type', 'text/plain'),
               ('Access-Control-Allow-Origin', '*'), 
               ('Access-Control-Allow-Methods', 'GET'),] 
    start_response("200 OK", headers)

    httphost = environ['REMOTE_ADDR']
    gets = dict(parse_qsl(environ.get('QUERY_STRING')))
    callback = gets.get('cb', '')
    
    if 'userinput' in gets:
        userinput = gets['userinput']
        
        if callback == 'get_suggestions':
            mark = gets['mark']
            num_results = gets['n']
            ret = cbGetSuggestionsHandler(userinput, httphost, mark=mark, num_results=num_results)
        elif callback == 'submit_query':
            ret = cbSubmitQueryHandler(userinput, httphost)
    elif callback == 'get_existing':
        ret = cbGetExistingQueries(httphost)

    if not isinstance(ret, list):
        ret = list(ret)
        
    return ret


if __name__ == '__main__':
    import sys
    from wsgiref.simple_server import make_server
    if len(sys.argv) > 1:
        port = sys.argv[2]
    else:
        port = 8080
    server = make_server('localhost', port, application)
    server.serve_forever()
