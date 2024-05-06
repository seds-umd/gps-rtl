SIM ?= icarus
WAVES = 1
TOPLEVEL_LANG ?= verilog

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ns

TOPLEVEL ?= $(DUT)
MODULE ?= test_$(DUT)

ifeq ($(SIM), verilator)
	EXTRA_ARGS += --trace-fst --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

waves: sim
	gtkwave sim_build/$(DUT).fst $(DUT).gtkw

all:
	@if grep -q "<failure />" "results.xml"; then exit 1; fi

spinal: $(PWD)/../../spinal/gps/$(DUT).scala
	cd $(PWD)/../../..; sbt $(SPINAL)
