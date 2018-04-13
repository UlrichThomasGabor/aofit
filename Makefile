ALL_IN_INTEGRATIONTEST := $(wildcard integration-tests/*)
DIRS := $(patsubst %/.,%,$(wildcard $(addsuffix /.,$(ALL_IN_INTEGRATIONTEST))))
all_files_in_integrationtests := $(filter-out $(DIRS),$(ALL_IN_INTEGRATIONTEST))
all_integrationtests := $(filter-out %.cmp,$(all_files_in_integrationtests))
all_integrationtest_targets := $(addsuffix .test, $(all_integrationtests))

all: test

test: $(all_integrationtest_targets)
	@echo "Success, all tests passed."

%.test: %.cmp
	$(basename $@) | diff -q $< - >/dev/null || (echo "Test $(basename $@) failed" && exit 1)

.PHONY: test all %.test
