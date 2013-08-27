"""
Lyle Scott, III
lyle@digitalfoo.net
http://digitalfoo.net

Copyright (c) 2012 Lyle Scott, III

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import json
import random

from flask import Flask
from flask import request
import mongotree


DEBUG = True

ALLOWED_METHODS = ('GET', 'PUT', 'DELETE', 'OPTIONS',)

app = Flask(__name__)


def index():
    """Return something on the root request.

    Returns:
        str. A random saying.
    """
    sayings = ('What are your intentions, human?',
               'Don\'t do that.',
               'Stop that!',
               'Go away, human.')

    return sayings[random.randint(0, len(sayings) - 1)]


def get_all_queries(identifier):
    """Get all queries.

    Arguments:
        identifier (str): Part of the key that will be associated with queries.

    Returns:
        list of str representing all queries in the system.
    """
    mtree = mongotree.MongoTree(identifier=identifier)

    nodes = []
    [nodes.extend(mtree.get_leaf_nodes(root)) for root in mtree.get_roots()]

    if not nodes:
        return json.dumps(['No autocompletes are available for identifier %s.'
                           % identifier])

    paths = [' '.join(node['path'].split(mtree.SEPARATOR)) for node in nodes]

    return json.dumps(paths)


def put_query(identifier):
    """Save a query to a prefix tree.

    Arguments:
        identifier (str): Part of the key that will be associated with queries.

    Returns:
        json'ified True.
    """
    query = request.form.get('query', '')

    mtree = mongotree.MongoTree(identifier=identifier)
    mtree.upsert(query.split())

    return json.dumps(True)


def options_for_suggestions(identifier):
    """Get suggestions based on the current query.

    Arguments:
        identifier (str): Part of the key that will be associated with queries.

    Returns:
        a list containing autocompletes; queries that could possibly
        autocomplete the current set of tokens.
    """

    print 'OPTIONS_FOR_SUGGESTIONS'

    try:
        n_results = json.loads(request.args.get('n'))
    except:
        n_results = 10

    try:
        mark = json.loads(request.args.get('mark'))
    except:
        mark = False

    n_results = request.args.get('n', -1)
    next_token_only = request.args.get('next_token_only', False)

    mtree = mongotree.MongoTree(identifier=identifier)
    query_ = request.args.get('query', '')
    query = query_.split()

    if not query_:
        path = ''
        token = ''
    elif query_[-1] == ' ':
        path = query
        token = ''
    elif len(query) == 1:
        path = ''
        token = query[0]
    else:
        path = query[:-1]

        if len(query) > 1:
            token = query[-1]
        else:
            token = ''

    print 'path "%s"' % path
    print 'token "%s"' % token

    node = mtree.get_node_by_path(path)

    foo = []

    if n_results:
        n = 0

    """
    TODO

    implement children only
    implement all nodes
    implement leaves only

    mark nodes as end nodes when saved
    """


    if node or (not path and token):

        if not path and token:
            children = mtree.get_roots()
        else:
            children = mtree.get_children(node['path'])

        for child in children:

            if n_results:
                n += 1
                if n == n_results:
                    break

            label = child['label']
            if not label.startswith(token):
                continue

            #if next_token_only:
            #    foo.append(label)
            #else:
            path = child['path'].split(mtree.SEPARATOR)
            foo.append(' '.join(path))

    if mark:
        mark_l = request.args.get('markL', '__MARKL__')
        mark_r = request.args.get('markR', '__MARKR__')

    print 'PATHS', foo

    return json.dumps(foo)


def delete_query(identifier):
    """Remove a query (and all subqueries) from the tree.

    Arguments:
        identifier (str): Part of the key that will be associated with queries.

    Returns:
        json'ified True.
    """
    query = request.form.get('query', '')

    mtree = mongotree.MongoTree(identifier=identifier)
    node = mtree.get_node_by_path(query)
    mtree.remove(node)

    return json.dumps(True)


@app.after_request
def after_request(response):
    """Let requests come from anywhere.

    Arguments:
        response (): The response object used by flask.

    Returns:
        The response (flask.wrappers.Response) object with Access-Control-Allow
        headers added.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = ','.join(ALLOWED_METHODS)

    return response


def attach_rules():
    """Associate a URI path to a view function."""
    app.add_url_rule('/',
                     view_func=index,
                     methods=ALLOWED_METHODS)

    get_all_queries.provide_automatic_options = False
    app.add_url_rule('/<identifier>',
                     view_func=get_all_queries,
                     methods=['GET'])

    options_for_suggestions.provide_automatic_options = False
    app.add_url_rule('/<identifier>',
                     view_func=options_for_suggestions,
                     methods=['OPTIONS'])

    put_query.provide_automatic_options = False
    app.add_url_rule('/<identifier>',
                     view_func=put_query,
                     methods=['PUT'])

    put_query.provide_automatic_options = False
    app.add_url_rule('/<identifier>',
                     view_func=delete_query,
                     methods=['DELETE'])


def run():
    """Gogo Python gadget!"""
    app.debug = DEBUG
    attach_rules()
    app.run()


if __name__ == '__main__':
    run()
