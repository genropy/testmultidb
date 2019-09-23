#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('client_contact_phone', pkey='id', name_long='!!Client contact phone')
        self.sysFields(tbl)
        tbl.column('client_contact_id',size='22' ,group='_',name_long='!!Client contact id').relation('client_contact.id',relation_name='morephones',mode='foreignkey',onDelete='cascade')
        tbl.column('phone_type' ,size=':1',name_long='!!Type',values='M:Mobile,H:Home')