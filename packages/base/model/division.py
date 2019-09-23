# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('division',pkey='code',name_long='division',
                        name_plural='division',caption_field='name',multidb='one')
        tbl.column('code',size=':5',name_long='Code')
        tbl.column('name',name_long='Name')


    def trigger_onInserted(self,record=None):
        #divisions are also dbstores so after insert it create a dbstore
        dbstore = record['code']
        dbname= 'testmultidb_%s' %dbstore
        self.db.stores_handler.add_dbstore_config(dbstore,dbname=dbname,save=True)


    def trigger_onDeleted(self,record=None):
        self.db.stores.drop_store(record['code'])


    def multidb_getForcedStore(self,record):
        return record['code']

    def pippo(self):
        print 'pippo'