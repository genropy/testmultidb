# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('client_type',pkey='id',name_long='client_type',
                            name_plural='client_type',
                            caption_field='id',lookup=True,multidb='*')
        self.sysFields(tbl)
        tbl.column('description',name_long='description')

    def sysRecord_SPECIAL(self):
        return self.newrecord(description='Special client')

    def sysRecord_AUTO(self):
        return self.newrecord(description='AUTO')