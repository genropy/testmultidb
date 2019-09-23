from gnr.app.gnrapp import GnrApp

db = GnrApp('sandboxpg').db
regione = db.table('glbl.provincia')
q = regione.query(checkPermissions=dict(user='fbollo',user_group='CONT'),columns='$sigla,$nome,$zona_regione',where='$regione=:r',r='LOM')
print q.sqltext
s = q.selection()
print s.output('grid')