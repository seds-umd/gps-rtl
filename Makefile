.PHONY: all test
all: test

test:
	./hw/tb/run_all.sh $(TESTS)
