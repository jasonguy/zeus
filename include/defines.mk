
PP = PYTHONPATH=$(PWD)/lib

TMPDIR = $(PWD)/tmp

BINDIR = $(PWD)/bin

PWCDIR = $(TMPDIR)/etc

PASSWORDCACHE = $(PWCDIR)/passwords.txt

SSHDIR = $(TMPDIR)/.ssh

SSHCONFIG = $(SSHDIR)/config

ifeq "$(CONFIGFILE)" ""
CONFIGFILE = $(PWD)/conf/allinone.yaml
endif

