
TMPDIR = $(PWD)/tmp

BINDIR = $(PWD)/bin

PASSWORDCACHE = $(TMPDIR)/passwords.txt

ifeq "$(CONFIGFILE)" ""
CONFIGFILE = $(PWD)/conf/allinone.yaml
endif

$(TMPDIR):
	mkdir -pv $(TMPDIR)

start: $(TMPDIR)
	@date > $(TMPDIR)/.START

$(PASSWORDCACHE): $(TMPDIR)
	$(BINDIR)/mkpwcache.sh "$(PASSWORDCACHE)"

passwordcache: $(PASSWORDCACHE)

preflight:
	@which fab 1>/dev/null 2>/dev/null

finish: $(TMPDIR)
	@date > $(TMPDIR)/.FINISH

clean:
	rm -rf $(TMPDIR)

