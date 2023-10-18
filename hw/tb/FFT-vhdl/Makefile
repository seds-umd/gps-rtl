# This is the name of the module in Verilog/VHDL
DUT = fft4096_wrapper1

# This is the name of the python file containing the testbench
MODULE = test_fft

VHDL_SOURCES += $(wildcard $(PWD)/../../vhdl/fpga-fft/rtl/*)
VHDL_SOURCES += $(wildcard $(PWD)/../../vhdl/fpga-fft/generated/fft4096/*)

# Simulator settings
TOPLEVEL_LANG = vhdl
SIM = ghdl

# Specify generics
SIM_ARGS += -gdataBits=8 -gtwBits=10 --fst=sim_build/dump.fst --ieee-asserts=disable

include ../common.mk
