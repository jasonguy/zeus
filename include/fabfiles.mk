
pingcheck:
	$(FABRIC)

connectcheck:
	$(FABRIC)

hostname:
	$(FABRIC)

newrelic:
	$(FABRIC)

cloudarchive:
	$(FABRIC)

distupgrade:
	$(FABRIC)

mysql:
	$(FABRIC)

rabbit:
	$(FABRIC)

memcached:
	$(FABRIC)

configeditor:
	$(FABRIC)

keystone:
	$(FABRIC)

# the openstack services defined in keystone, not the keystone systemd service in the controller node
keystone_services:
	$(FABRIC)

glance:
	$(FABRIC)

nova_controller:
	$(FABRIC)

