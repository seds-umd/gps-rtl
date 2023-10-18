# This is the name of the module in Verilog/VHDL
DUT = fft4096_wrapper1

# This is the name of the python file containing the testbench
MODULE = test_fft

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../vhdl/fft-verilog/fft4096_processed.v

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
