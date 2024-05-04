# This is the name of the module in Verilog/VHDL
DUT = Decimate

# This is the name of the python file containing the testbench
MODULE = test_decimate

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../gen/$(DUT).v $(PWD)/../../verilog/*.v

SPINAL = "runMain gps.DecimateVerilog"

spinal: $(PWD)/../../spinal/gps/Decimate.scala
	cd $(PWD)/../../..; sbt $(SPINAL)

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
