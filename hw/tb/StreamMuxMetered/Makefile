DUT = StreamMuxMetered
TOPLEVEL = StreamMuxMeteredTest

# This is the name of the python file containing the testbench
MODULE = test_streammuxmetered

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../gen/$(DUT)Test.v
SPINAL = "runMain gps.StreamMuxMeteredVerilog"
FST_FILE = sim_build/StreamMuxMeteredTest.fst

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
