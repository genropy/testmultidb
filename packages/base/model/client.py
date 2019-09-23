# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('client',pkey='id',
                        name_long='client',
                        name_plural='client',
                        caption_field='fullname',multidb=True,
                        multidb_onLocalWrite='merge')
        self.sysFields(tbl)
        tbl.column('fullname',name_long='Full name')
        tbl.column('address',name_long='Address')
        tbl.column('type_id',size='22',name_long='Type').relation('client_type.id',relation_name='clients', mode='foreignkey', onDelete='raise')


    def sysRecord_AUTO(self):
        return self.newrecord(fullname='AUTO CLIENT',address='XXX',
                            type_id=self.db.table('base.client_type').sysRecord('AUTO')['id'])