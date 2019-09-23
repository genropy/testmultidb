# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('product_type',pkey='id',name_long='product_type',
                        name_plural='product_type',caption_field='description',multidb=True)
        self.sysFields(tbl,hierarchical='description',counter=True)
        tbl.column('description',name_long='description')
