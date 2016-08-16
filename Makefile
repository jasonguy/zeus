
#
# ゼウス
#

include include/defines.mk

all: $(ALL)

include include/targets.mk
include include/fabfiles.mk

ci: clean all

fabtargets:
	bin/mkfabtargets.sh > include/fabfiles.mk

preload:
	make $(SSHCONFIG)
	make $(PASSWORDCACHE)
