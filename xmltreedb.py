"""
Lyle Scott, III
lyle@digitalfoo.net
http://digitalfoo.net
"""

from datetime import datetime
from sqlalchemy import *
from sqlalchemy import exceptions


class XmltreeDB():
    """An interface for storing, retrieving, and updating xmltrees for a unique
    uuid.
    """
    
    def __init__(self, engine):
        """Initialize DB connection."""
        self.engine = engine
        self.db = create_engine(self.engine)
        self.metadata = MetaData(self.db)
        
    def _get_table(self, tablename):
        """Helper function to get the handle to an existing table handle or
        create one if it does not exist.
        """
        try:
            tbl = Table(tablename, self.metadata, autoload=True)
        except exceptions.NoSuchTableError:
            self.create_tables(tablenames=tablename)
            tbl = Table(tablename, self.metadata, autoload=True)

        if tbl is None:
            raise ValueError('_get_table: could not find or create %s' %
                             tablename) 
        
        return tbl
   
    def _uuid_exists(self, uuid):
        """Return true if the uuid exists in the DB, false if not."""
        xmltrees_tbl = self._get_table('xmltrees')
        query = select([xmltrees_tbl,], xmltrees_tbl.c.uuid==uuid)
        result = query.execute()
        
        return bool(result.rowcount)
        
    def create_tables(self, tablenames=None):
        """Create a table with the correct column info."""
        
        # Ensure tablenames is a datatype that supports a proper IN method.    
        if tablenames and (not isinstance(tablenames, list) and
                           not isinstance(tablenames, tuple)):
            tablenames = (tablenames,)
            
        if not tablenames or 'xmltrees' in tablenames:
            Table('xmltrees', self.metadata,
                Column('_uuid', Integer, primary_key=True),
                Column('uuid', String(255), primary_key=True),
                Column('xmltree', Text),
                Column('created', DateTime),
                Column('modified', DateTime))
        
        self.metadata.create_all(self.db)
        
    def save_xmltree(self, uuid, xmltree):
        """Put the xmltree for an uuid."""
        xmltrees_tbl = self._get_table('xmltrees')
        now = datetime.now()
        
        # If it exists, update the xmltree for the uuid. Otherwise, create a
        # new row for the uuid.
        if self._uuid_exists(uuid):
            values = {xmltrees_tbl.c.xmltree: xmltree,
                      xmltrees_tbl.c.modified: now}
            wheres = (xmltrees_tbl.c.uuid==uuid,)
            q = xmltrees_tbl.update().values(values).where(*wheres)
        else:
            values = {xmltrees_tbl.c.uuid: uuid,
                      xmltrees_tbl.c.xmltree: xmltree,
                      xmltrees_tbl.c.created: now,
                      xmltrees_tbl.c.modified: now,} 
            q = xmltrees_tbl.insert().values(values)
        
        result = q.execute()
            
        if result:
            return 'success'
        else:
            return 'error'
        
    def load_xmltree(self, uuid):
        """Get the xmltree for an uuid."""
        xmltrees_tbl = self._get_table('xmltrees')
        
        query = select([xmltrees_tbl.c.xmltree,],
                        xmltrees_tbl.c.uuid==uuid)
        result = query.execute()
        
        l = result.rowcount
        if l == 0:
            return {'error': 'load_xmltree --> no xmltree found for key %s' %
                    uuid}
        elif l == 1:
            row = result.fetchone()
            return row[0]
        else:
            return {'error', 'load_xmltree --> unknown error.'}
