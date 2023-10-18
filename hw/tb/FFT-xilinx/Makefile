# This is the name of the module in Verilog/VHDL
DUT = XilinxFFT

# This is the name of the python file containing the testbench
MODULE = test_fft

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../verilog/$(DUT).v

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
