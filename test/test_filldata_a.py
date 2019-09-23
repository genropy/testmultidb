from gnr.app.gnrapp import GnrApp
import pytest


def setup_module(module):
    module.INSTANCE_NAME = 'testmultidb'

class TestFillMultidbData:
    def setup_class(cls):
        cls.app = GnrApp(INSTANCE_NAME)
        cls.db = cls.app.db
        for s in cls.db.stores_handler.dbstores.keys():
            cls.db.stores_handler.drop_store(s)
        try:
            cls.db.dropDb(cls.db.dbname)
        except Exception:
            pass
        cls.db.checkDb()
        cls.db.model.applyModelChanges()
        cls.client_type_foo_rec = dict(description='Foo')
        cls.product_type_rec_1 = dict(description='Type One')
        cls.product_type_rec_2 = dict(description='Type Two',__multidb_default_subscribed=True)
        cls.product_type_rec_3 = dict(description='Type Three')
        subscription_tbl = cls.db.table('multidb.subscription')
        cls.subscription_tbl = subscription_tbl

    def test_creating_store(self):
        divtable = self.db.table('base.division')
        divtable.insert(dict(code='div_a',name='Albuquerque'))
        divtable.insert(dict(code='div_b',name='Boston'))
        self.db.commit()
        assert 'div_a' in self.db.dbstores,'Add store did not work'

    def test_sync_one(self):
        divtable = self.db.table('base.division')
        divisions = divtable.query().fetch()
        assert len(divisions)==2,'Error in mainstore data'
        with self.db.tempEnv(storename='div_b'):
            divisions = divtable.query().fetch()
            assert len(divisions)==1 and divisions[0]['code']=='div_b','Error in syncstore data'
            with pytest.raises(divtable.multidbExceptionClass()):
                divtable.insert(dict(name='NOINSERT',code='ERR'))
            with pytest.raises(divtable.multidbExceptionClass()):
                with divtable.recordToUpdate(code='div_b') as rec:
                    rec['name'] = 'Busta'

    def test_sync_all_insert(self):
        cli_type = self.db.table('base.client_type')
        cli_type.insert(self.client_type_foo_rec)
        cli_type.insert(dict(description='Bar'))
        cli_type.insert(dict(description='Span'))
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            f = cli_type.query().fetch()
            assert len(f)==3, 'sync all insert does not work'
            with pytest.raises(cli_type.multidbExceptionClass()):
                cli_type.insert(dict(description='NOINSERT'))

    def test_sync_all_update(self):
        cli_type = self.db.table('base.client_type')
        with cli_type.recordToUpdate(self.client_type_foo_rec['id']) as rec:
            rec['description'] = 'Fooss'
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            localdesc = cli_type.readColumns(pkey=self.client_type_foo_rec['id'],columns='$description')
            assert localdesc=='Fooss', 'sync all upd does not work'
            with pytest.raises(cli_type.multidbExceptionClass()):
                with cli_type.recordToUpdate(self.client_type_foo_rec['id']) as rec:
                    rec['description'] = 'Fonzie'

    def test_sync_all_delete(self):
        cli_type = self.db.table('base.client_type')
        cli_type.delete(self.client_type_foo_rec)
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            f = cli_type.query().fetch()
            assert len(f)==2, 'sync all delete does not work'
            with pytest.raises(cli_type.multidbExceptionClass()):
                cli_type.delete(f[0]['id'])

    def test_sync_partial_default_subscription(self):
        product_type_tbl = self.db.table('base.product_type')
        product_type_tbl.insert(self.product_type_rec_1)
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            f = product_type_tbl.query().fetch()
            assert len(f)==0, 'it should not insert in local store'
        with product_type_tbl.recordToUpdate(pkey=self.product_type_rec_1['id']) as rec:
            rec['__multidb_default_subscribed'] = True
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            assert product_type_tbl.existsRecord(self.product_type_rec_1['id']),'__multidb_default_subscribed is not working'
        with self.db.tempEnv(storename='div_b'):
            assert product_type_tbl.existsRecord(self.product_type_rec_1['id']),'__multidb_default_subscribed is not working'
        with pytest.raises(product_type_tbl.multidbExceptionClass()):
            with product_type_tbl.recordToUpdate(pkey=self.product_type_rec_1['id']) as rec:
                rec['__multidb_default_subscribed'] = False
        product_type_tbl.insert(self.product_type_rec_2)
        self.db.commit()       
        with self.db.tempEnv(storename='div_a'):
            assert product_type_tbl.existsRecord(self.product_type_rec_2['id']),'__multidb_default_subscribed is not working'
        with self.db.tempEnv(storename='div_b'):
            assert product_type_tbl.existsRecord(self.product_type_rec_2['id']),'__multidb_default_subscribed is not working'
        product_type_tbl.delete(self.product_type_rec_2)
        self.db.commit()
        with self.db.tempEnv(storename='div_b'):
            assert not product_type_tbl.existsRecord(self.product_type_rec_2['id']),'__multidb_default_subscribed is not working'

    def test_sync_partial_explicit_subscription(self):
        product_type_tbl = self.db.table('base.product_type')
        product_tbl = self.db.table('base.product')
        product_type_tbl.insert(self.product_type_rec_3)
        product_type_id = self.product_type_rec_3['id']
        product_rec = dict(code='T1',description='Test One',product_type_id=product_type_id)
        product_tbl.insert(product_rec)
        self.db.commit()
        product_tbl.multidbSubscribe(product_rec['id'],dbstore='div_b')
        self.db.commit()
        with self.db.tempEnv(storename='div_b'):
            assert product_tbl.existsRecord(product_rec['id']),'explicit subscription is not working'
            assert product_type_tbl.existsRecord(self.product_type_rec_3['id']),'autosubscription of ascending relation is not working'
        with self.db.tempEnv(storename='div_a'):
            assert not product_tbl.existsRecord(product_rec['id']),'explicit subscription is not working'
        with pytest.raises(product_tbl.multidbExceptionClass()):
            with self.db.tempEnv(storename='div_b'):
                with product_tbl.recordToUpdate(pkey=product_rec['id']) as rec:
                    rec['description'] = 'Test fail'
        with pytest.raises(product_tbl.multidbExceptionClass()):
            with self.db.tempEnv(storename='div_a'):
                product_tbl.insert(dict(code='T2',description='Do not'))
        with self.db.tempEnv(storename='div_b'):
            product_tbl.delete(product_rec)
        subtbl = self.db.table('multidb.subscription')
        assert not subtbl.checkDuplicate(dbstore='div_b',tablename='base.product',
                                        **{subtbl.tableFkey(product_tbl):product_rec['id']}),'subscription should be erased'
        subtbl.deleteSelection(where='$dbstore=:d AND $tablename=:t AND $%s=:p' %subtbl.tableFkey(product_type_tbl),d='div_b',t='base.product_type',p=product_type_id)
        with self.db.tempEnv(storename='div_b'):
            assert not product_type_tbl.existsRecord(product_type_id),'unsubscription is not working'


    def test_sync_parent_subscription(self):
        cli_type = self.db.table('base.client_type')
        cli_type_rec = dict(description='Extra')
        cli_type.insert(cli_type_rec)
        client_tbl = self.db.table('base.client')
        client_contact_tbl = self.db.table('base.client_contact')
        client_contact_phone_tbl = self.db.table('base.client_contact_phone')
        client_rec = dict(fullname='Smiths inc.',address='112 Coke street Brooklin',
                                type_id=cli_type_rec['id'])
        client_tbl.insert(client_rec)
        client_id = client_rec['id']
        contact_1 = dict(name='Kip Thorne',mainphone='+55522009',client_id=client_id)
        contact_2 = dict(name='Meredith Smith',mainphone='+55532109',client_id=client_id)
        contact_3 = dict(name='Div b only',mainphone='+272727',client_id=client_id)
        client_contact_tbl.insert(contact_1)
        client_contact_tbl.insert(contact_2)
        ccp = dict(client_contact_id=contact_1['id'],phone='6289994',phone_type='H')
        client_contact_phone_tbl.insert(ccp)
        self.db.commit()
        client_tbl.multidbSubscribe(client_rec['id'],dbstore='div_a')
        client_tbl.multidbSubscribe(client_rec['id'],dbstore='div_b')
        self.db.commit()
        with self.db.tempEnv(storename='div_b'):
            assert client_contact_tbl.existsRecord(contact_1['id']),'multidb parent is not working'
            assert client_contact_tbl.existsRecord(contact_2['id']),'multidb parent is not working'
            assert client_contact_phone_tbl.existsRecord(ccp['id']),'multidb parent parent is not working'
            with pytest.raises(client_contact_tbl.multidbExceptionClass()):
                client_contact_tbl.delete(contact_2)
            client_contact_tbl.insert(contact_3)
        self.db.commit()
        with self.db.tempEnv(storename='div_b'):
            client_contact_tbl.delete(contact_3)
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            assert client_contact_tbl.existsRecord(contact_2['id']),'multidb parent is not working'
            with client_contact_tbl.recordToUpdate(contact_1['id']) as rec_div_a:
                rec_div_a['mainphone'] = '1800starwars'
        self.db.commit()
        with client_contact_tbl.recordToUpdate(contact_1['id']) as rec:
            rec['name'] = 'Kip Thorne changed'
        self.db.commit()
        with self.db.tempEnv(storename='div_a'):
            name,mainphone = client_contact_tbl.readColumns(pkey=contact_1['id'],columns='$name,$mainphone')
            assert name=='Kip Thorne changed' and mainphone=='1800starwars','Merge parent failed'

    def test_sync_partial_explicit_subscription_merge(self):
        client_tbl = self.db.table('base.client')
        client_rec = client_tbl.record(fullname='Smiths inc.').output('dict')
        with self.db.tempEnv(storename='div_b'):
            with client_tbl.recordToUpdate(client_rec['id']) as r:
                r['address'] = '312 Pepsi Adelaide'
        self.db.commit()
        with client_tbl.recordToUpdate(client_rec['id']) as r:
            r['fullname'] =  'Smiths & Sons'
            r['address'] = 'Address changed'
        self.db.commit()
        client_rec_main = client_tbl.record(client_rec['id']).output('dict')
        client_rec_local = client_tbl.record(client_rec['id'],_storename='div_b').output('dict')
        assert client_rec_main['fullname'] == client_rec_local['fullname'] \
                and client_rec_main['address']!= client_rec_local['address'],'Marge partial failed'
        with self.db.tempEnv(storename='div_b'):
            with client_tbl.recordToUpdate(client_rec['id']) as r:
                r['address'] = 'Address changed'
        with client_tbl.recordToUpdate(client_rec['id']) as r:
            r['fullname'] =  'Smiths & Sons'
            r['address'] = 'Address changed again'
        client_rec_main = client_tbl.record(client_rec['id']).output('dict')
        client_rec_local = client_tbl.record(client_rec['id'],_storename='div_b').output('dict')
        assert client_rec_main['fullname'] == client_rec_local['fullname'] \
                and client_rec_main['address'] == client_rec_local['address'],'Marge partial failed'

    def test_sync_all_sysrecord(self):
        cli_type = self.db.table('base.client_type')
        type_id = None
        with self.db.tempEnv(storename='div_a'):
            type_id = cli_type.sysRecord('SPECIAL')['id']
        assert type_id is not None, 'sysrecord not created'
        assert len(cli_type.query(where='$id=:type_id',type_id=type_id).fetch())>0,'sysrecord not created in mainstore'
        with self.db.tempEnv(storename='div_b'):
            assert len(cli_type.query(where='$id=:type_id',type_id=type_id).fetch())>0,'sysrecord not created in sibling'

    def test_sync_partial_sysrecord(self):
        client = self.db.table('base.client')
        client_id = None
        with self.db.tempEnv(storename='div_a'):
            auto_client = client.sysRecord('AUTO')
            client_id = auto_client['id']
            assert auto_client['__multidb_default_subscribed'],'default subscribed sysrecord partial'
        assert client_id is not None, 'sysrecord not created'
        assert len(client.query(where='$id=:client_id',client_id=client_id).fetch())>0,'sysrecord not created in mainstore'
        with self.db.tempEnv(storename='div_b'):
            assert len(client.query(where='$id=:client_id',client_id=client_id).fetch())>0,'sysrecord not created in sibling'
