DUT = [dut name here]

# This is the name of the python file containing the testbench
MODULE = test_[dut name]

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../gen/$(DUT).v

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
