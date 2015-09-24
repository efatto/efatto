import erppeek
client = erppeek.Client('http://localhost:8069')

client.create_database('super_password', 'demo')
# client.db.list()
# client.modules(installed=True)
# len(client.modules()['uninstalled'])
model('res.users').create({'login': 'joe', 'name': 'Joe'})
