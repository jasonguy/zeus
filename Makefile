
include include/defines.mk

all: start preflight $(PASSWORDCACHE) $(SSHCONFIG)

include include/targets.mk

