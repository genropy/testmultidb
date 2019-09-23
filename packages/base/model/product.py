# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('product',pkey='id',name_long='product',name_plural='product',caption_field='description',multidb=True)
        self.sysFields(tbl)
        tbl.column('code',size=':10',name_long='code')
        tbl.column('description',name_long='description')
        tbl.column('product_type_id',size='22',name_long='Type').relation('product_type.id',relation_name='products', mode='foreignkey', onDelete='raise')
