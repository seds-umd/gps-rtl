VHDL_RTL = ../fpga-fft/rtl
VHDL_GEN = ../fpga-fft/generated/fft4096

add:
	ghdl -i $(VHDL_RTL)/* $(VHDL_GEN)/*
	ghdl -m fft4096_wrapper1

synth:
	ghdl --synth -gdataBits=8 -gtwBits=10 --out=verilog fft4096_wrapper1 > fft4096.v
