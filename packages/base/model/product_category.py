# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('product_category', pkey='code', name_long='Product category',multidb='*')
        self.sysFields(tbl,id=False)
        tbl.column('code', size=':10', name_long='Cat.Code')
        tbl.column('description', size=':40', name_long='Cat.Desc')

    def trigger_onInserting(self,record):
        if record['code']=='CA':
            raise 