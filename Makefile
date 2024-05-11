TBS = Decimate FFT-xilinx Magnitude MagnitudeStream MaxInterface Mixer PRN StreamDemuxMetered StreamMemory StreamMuxMetered
SUBDIRS = $(addprefix hw/tb/,$(TBS))

all: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ sim

.PHONY: all $(SUBDIRS)
