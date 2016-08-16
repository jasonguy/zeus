
ALL = start preflight $(PASSWORDCACHE) $(SSHCONFIG) pingcheck connectcheck hostname newrelic cloudarchive distupgrade \
			mysql rabbit memcached configeditor keystone keystone_services glance nova_controller finish

PP = PYTHONPATH=$(PWD)/lib

STAGES = stages

TMPDIR = $(PWD)/tmp

BINDIR = $(PWD)/bin

PWCDIR = $(TMPDIR)/etc

PASSWORDCACHE = $(PWCDIR)/passwords.txt

SSHDIR = $(TMPDIR)/.ssh

SSHCONFIG = $(SSHDIR)/config

ifeq "$(CONFIGFILE)" ""
CONFIGFILE = $(PWD)/conf/allinone.yaml
endif

CC = CONFIGFILE="$(CONFIGFILE)"
TT = TMPDIR="$(TMPDIR)"
PW = PASSWORDCACHE="$(PASSWORDCACHE)"
FS = --ssh-config-path=$(SSHCONFIG) --disable-known-hosts --user=root
FF = --fabfile $(STAGES)/$(@)/fabfile.py

FABRIC = $(CC) $(TT) $(PW) $(PP) fab $(FS) $(FF) $(@)

