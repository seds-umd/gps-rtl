# This is the name of the module in Verilog/VHDL
DUT = Magnitude

# This is the name of the python file containing the testbench
MODULE = test_magnitude

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../gen/$(DUT).v

SPINAL = "runMain gps.MagnitudeVerilog"

spinal: $(PWD)/../../spinal/gps/Magnitude.scala
	cd $(PWD)/../../..; sbt $(SPINAL)

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
