#!/usr/bin/env python

#import os
import sys

#sys.path.append(os.path.dirname(__file__))
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')

from urlparse import parse_qsl
import xmltree
import json

def cbGetSuggestionsHandler(userinput):
    """Callback handler for get_suggstions."""
    
    xtree = xmltree.XMLTree()
    xtree.insert_query(xtree.root, 'select * from derp')
    xtree.insert_query(xtree.root, 'select * from yeah')
    
    nodes, token = xtree.get_query_parts(userinput)

    results = xtree.get_autocompletes(nodes)
    results = ['%s %s' % (nodes, result,) for result in results]

    return 'get_suggestions({"results": %s})' % json.dumps(results)    


def application(environ, start_response):
    """Basically, fire off the callback handler."""
    headers = [('Content-type', 'text/plain'),
               ('Access-Control-Allow-Origin', '*'), 
               ('Access-Control-Allow-Methods', 'GET'),] 
    start_response("200 OK", headers)

    gets = dict(parse_qsl(environ.get('QUERY_STRING')))
    if 'userinput' in gets:
        userinput = gets['userinput']
        callback = gets.get('cb', '')
        
        if callback == 'get_suggestions':
            ret = cbGetSuggestionsHandler(userinput)
        elif callback == 'submit_query':
            pass

    if not isinstance(ret, list):
        ret = list(ret)
        
    return ret


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 8080, application)
    server.serve_forever()
