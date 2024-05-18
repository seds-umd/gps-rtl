TBS = Decimate FFT-xilinx Magnitude MagnitudeStream MaxInterface MaxMagnitude Mixer PRN StreamDemuxMetered StreamMemory StreamMuxMetered UartControl
SUBDIRS = $(addprefix hw/tb/,$(TBS))

all: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ sim

.PHONY: all $(SUBDIRS)
