import json
import random

from flask import Flask
from flask import request
from flask.ext.pymongo import PyMongo
from flask.ext.pymongo import ObjectId
from datetime import datetime

import xmltree

DEBUG = True

BLANK_XML_DOC = "<?xml version='1.0' encoding='utf-8'?><querytree/>"
ALLOWED_OPTIONS = ('GET', 'PUT', 'DELETE', 'OPTIONS',)

app = Flask(__name__)
mongo = PyMongo(app)

@app.after_request
def after_request(response):
    """Let requests come from anywhere."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = ','.join(ALLOWED_OPTIONS)

    return response

def getXml(identifier):
    """Get the XML associated with a specific identifier."""
    results = mongo.db.xmltrees.find_one({'id': identifier,})
    if not results:
        return BLANK_XML_DOC
     
    return results['xml']

def saveXml(identifier, xml):
    """Save the XML associated with a specific identifier."""
    now = datetime.now()
    where = {'id': identifier,}
    values = {'xml': xml, 'modified': now,}

    # One-offs that pertain to new vs existing records.
    #if not mongo.db.xmltrees.find_one(where):
    #    print 'FIND ONE ZOMG HAX'
    values['id'] = identifier
    existing = mongo.db.xmltrees.find_one(where)
    if existing:
        values['created'] = existing['created']
    else:
        values['created'] = now
    
    app.logger.debug('saveXml(identifier=%s, xml=%s)' % (identifier, xml,))
    app.logger.debug('saveXml: where=%s' % where)
    app.logger.debug('saveXml: values=%s' % values)
    
    mongo.db.xmltrees.update(where, values, upsert=True)

@app.route('/')
def index():
    print 'index'
    sayings = ('What are your intentions, human?',
               'Don\'t do that.',
               'Stop that!',
               'Go away, human.',)
    
    return sayings[random.randint(0, len(sayings)-1)]

@app.route('/id/')
def intellitypeindex():
    index()

@app.route('/id/<identifier>/', methods=['OPTIONS',])
def cbGetSuggestions(identifier):
    """TODO"""
    xml = getXml(identifier)
    xtree = xmltree.XMLTree(xml)

    next_token_only = request.form.get('next_token_only', False)
    n_results = request.form.get('n', 10)
    query = request.args.get('query')

    nodes, token = xtree.get_query_parts(query)
    results = xtree.get_autocompletes(nodes, token, mark=True,
                                      n_results=n_results,
                                      next_token_only=next_token_only)
       
    return json.dumps(results)      
    
@app.route('/id/<identifier>/', methods=['PUT',])
def cbSaveQuery(identifier):
    """TODO"""
    query = request.form.get('query')
    xml = getXml(identifier)
    xtree = xmltree.XMLTree(xml)
    xtree.insert_query(xtree.root, query)
    xml = xtree.get_xml(pretty_print=False)
    saveXml(identifier, xml)
    
    return json.dumps(True)

@app.route('/id/<identifier>/', methods=['GET',])
def cbGetExistingQueries(identifier):
    """TODO"""
    xml = getXml(identifier)
    xtree = xmltree.XMLTree(xml)
    paths = xtree.get_children_queries(xtree.root)
 
    return json.dumps(paths)

@app.route('/id/<identifier>/', methods=['DELETE',])
def delete(identifier):
    print 'DELETE'
    return ''


if __name__ == '__main__':
    app.debug = DEBUG
    app.run()
