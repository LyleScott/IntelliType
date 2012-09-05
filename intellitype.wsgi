#!/usr/bin/env python

import os
#import sys

#sys.path.append(os.path.dirname(__file__))
#sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')


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
    
def cbGetSuggestionsHandler(userinput, httphost, mark=False):
    """Callback handler for get_suggestions."""
    xmlfile = getXmlFile(httphost)
    xml = xmlfile.read()
    xtree = xmltree.XMLTree(xml)
    nodes, token = xtree.get_query_parts(userinput)
    results = xtree.get_autocompletes(nodes, token)
    
    _results = []
    for result in results:
        if mark:
            nodes = '__MARK_START__%s' % nodes
            result = result.replace(token, '%s__MARK_END__' % token)
            _results.append('%s %s' % (nodes, result,))
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

def application(environ, start_response):
    """Basically, fire off the callback handler."""
    headers = [('Content-type', 'text/plain'),
               ('Access-Control-Allow-Origin', '*'), 
               ('Access-Control-Allow-Methods', 'GET'),] 
    start_response("200 OK", headers)

    httphost = environ['REMOTE_ADDR']

    gets = dict(parse_qsl(environ.get('QUERY_STRING')))
    if 'userinput' in gets:
        userinput = gets['userinput']
        callback = gets.get('cb', '')
        
        if callback == 'get_suggestions':
            ret = cbGetSuggestionsHandler(userinput, httphost, mark=True)
        elif callback == 'submit_query':
            ret = cbSubmitQueryHandler(userinput, httphost)

    if not isinstance(ret, list):
        ret = list(ret)
        
    return ret


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 8080, application)
    server.serve_forever()
