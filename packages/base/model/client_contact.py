# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('client_contact',pkey='id',
                        name_long='client_contact',
                        name_plural='client_contact',caption_field='id')
        self.sysFields(tbl)
        tbl.column('client_id',size='22',name_long='Client').relation('client.id',relation_name='contacts', mode='foreignkey', onDelete='cascade')
        tbl.column('name',name_long='Name')
        tbl.column('mainphone',name_long='Phone')
