# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('document',pkey='id',name_long='document',name_plural='document',caption_field='id')
        self.sysFields(tbl)
        tbl.column('name',name_long='name')
        tbl.column('description',name_long='description')
