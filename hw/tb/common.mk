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

FST_FILE ?= sim_build/$(TOPLEVEL).fst
SCALA_FILE ?= $(DUT).scala
SPINAL ?= "runMain gps.$(DUT)Verilog"

waves:
	gtkwave $(FST_FILE) $(DUT).gtkw

# cocotb 1.x can return zero even when an assertion failed. Check its result
# after simulation, including missing, malformed and entirely skipped results.
define check_for_results_file
    @python "$(PWD)/../../../scripts/check_results.py" "$(COCOTB_RESULTS_FILE)"
endef

spinal: $(PWD)/../../spinal/gps/$(SCALA_FILE)
	cd $(PWD)/../../..; sbt $(SPINAL)

$(PWD)/../../gen/$(TOPLEVEL).v: $(PWD)/../../spinal/gps/$(SCALA_FILE)
	cd $(PWD)/../../..; sbt $(SPINAL)
