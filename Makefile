
#
# ゼウス
#

include include/defines.mk

all: $(ALL)

include include/targets.mk
include include/fabfiles.mk

ci: clean all

