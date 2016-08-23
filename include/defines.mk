
ALL = start \
			preflight $(PASSWORDCACHE) $(SSHCONFIG) \
			pingcheck connectcheck \
			hostname newrelic cloudarchive distupgrade \
			mysql rabbit memcached configeditor \
			keystone keystone_services glance nova_controller nova_compute neutron nova_controller_post_neutron dashboard \
			zookeeper cassandra midonet_cluster midonet_agent midonet_analytics midonet_manager \
			finish

PP = PYTHONPATH=$(PWD)/lib

STAGES = stages

TMPDIR = $(PWD)/tmp

BINDIR = $(PWD)/bin

PWCDIR = $(TMPDIR)/etc

PASSWORDCACHE = $(PWCDIR)/passwords.txt

SSHDIR = $(TMPDIR)/.ssh

SSHCONFIG = $(SSHDIR)/config

ifeq "$(CONFIGFILE)" ""
CONFIGFILE = $(PWD)/conf/benningen.yaml
endif

CC = CONFIGFILE="$(CONFIGFILE)"
TT = TMPDIR="$(TMPDIR)"
PW = PASSWORDCACHE="$(PASSWORDCACHE)"
FS = --ssh-config-path=$(SSHCONFIG) --disable-known-hosts --user=root
FF = --fabfile $(STAGES)/$(@)/fabfile.py

FABRIC = $(CC) $(TT) $(PW) $(PP) fab $(FS) $(FF) $(@)

