DUT = MagnitudeStream
TOPLEVEL = MagnitudeStreamWrapper
SCALA_FILE = Magnitude.scala

# This is the name of the python file containing the testbench
MODULE = test_magnitude_stream

# This is a list of all Verilog files needed, can also use VHDL_SOURCES
VERILOG_SOURCES = $(PWD)/../../gen/$(TOPLEVEL).v

# Simulator settings
TOPLEVEL_LANG = verilog
SIM = icarus

include ../common.mk
