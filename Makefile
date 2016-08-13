
include include/defines.mk

all: start preflight $(PASSWORDCACHE) $(SSHCONFIG) pingcheck connectcheck

include include/targets.mk
include include/fabfiles.mk

