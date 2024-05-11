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

FST_FILE ?= sim_build/$(DUT).fst
SPINAL ?= "runMain gps.$(DUT)Verilog"

waves: sim
	gtkwave $(FST_FILE) $(DUT).gtkw

all:
	@if grep -q "<failure />" "results.xml"; then exit 1; fi

spinal: $(PWD)/../../spinal/gps/$(DUT).scala
	cd $(PWD)/../../..; sbt $(SPINAL)

$(PWD)/../../gen/$(DUT).v: spinal
