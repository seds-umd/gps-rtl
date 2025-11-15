#!/usr/bin/env python3

import numpy as np
import socket
import struct
import time
import threading

# Acquisition expects ComplexTimestamp = {re: SInt(2), im: SInt(2), timestamp: UInt(12)}
# Tb -> StreamWidthAdapter(Stream(Bits(8 bits)), Stream(Bits(16 bits))) -> 2 bytes/sample

FPGA_IP   = ""     # FPGA IP address
PC_IP     = ""     # PC IP address

PORT_CTRL = 0      # AXI-Lite read/write
PORT_IQ   = 0      # Send samples + receive acquisition results

PRN_ID = 1
fs = 1_000_000        
# The FPGA acquisition testbench expects a simplified model: ~1 sample per C/A chip
#
# GPS C/A code = 1023 chips (1 ms)
# The FPGA's FFT size is 4096, and its internal PRN length is 4092 = 1023 × 4
#
# So we need to generate a signal so that:
#   - fs ≈ 1 MHz -> ~1 sample per chip
#   - 4092 samples per acquisition block -> represents 4 ms of repeated PRN
#   - timestamps that roll over every 4092 samples (FPGA requirement)
#
# (This is only for the testbench model, not real GPS front-end sampling)

chip_rate = 1_023_000    # GPS C/A
duration_ms = 20         # 20 ms = 5 acquisition windows
doppler = 4000           # Hz
period = 4092            # Timestamp rollover

# L1 signal transmitted by satellite (purely real):
# RF(t) = PRN(t) × cos(2π (1575.42 MHz + Doppler) t)

# MAX2769 (or this Python script) converts the real RF signal
# into complex baseband by mixing with cosine and sine:

# I(t) = RF(t) × cos(2π 1575.42 MHz t)
# Q(t) = RF(t) × sin(2π 1575.42 MHz t)

# -> look into why we need a complex signal 

# After low-pass filtering and combining I(t) + j Q(t),
# the 1575.42 MHz carrier is removed -> only Doppler shift left

# Resulting complex baseband signal is:
# baseband(t) = PRN(t) × exp(j · 2π · Doppler · t)



# Generate C/A PRN code
# https://www.wasyresearch.com/generating-gps-l1-c-a-pseudo-random-noise-prn-code-with-matlab-and-c-c/
def generate_ca_prn(prn_id):
    # GPS C/A code uses two 10-bit LFSRs

    # Tap positions depend on PRN_ID
    #   Example: PRN 1 -> G1(10) XOR (G2(2) XOR G2(6))

    # Output chip = G1_last_bit  XOR  (G2_tap1 XOR G2_tap2)

    # G1 taps (10,3)
    # New bit = XOR(all tapped bits)

    # G2 taps (10, 9, 8, 6, 3, 2)

    # Convert {0,1} to {+1, -1}
    # TODO: implement
    pass



# Generate baseband complex signal 
# baseband_signal(t) = PRN(t) × exp(j.2pi.doppler.t)
# Python takes samples of this continuous signal at times t = 0, 1/fs, 2/fs, 3/fs...
# complex_sample[n] = chip_value(t_n) × exp(j.2pi.doppler.t_n)
#
# L1 frequency = 1575.42 MHz
# Received frequency = 1575.42 MHz + Doppler (up to +/-5 kHz)
# After MAX2769 downconverts to baseband, Doppler shift shows up 
# as a slow rotation of the complex baseband I/Q samples
def generate_baseband_signal(prn_id, duration_ms):
    # generate prn -> returns 1023 chips of +1 and –1
    # calculate how many samples we need to send
    # repeat PRN chips that many times

    # t = 0, 1/fs, 2/fs, 3/fs...

    # Complex sinusoid rotating at 4000 Hz
    # exp(jθ) = cos(θ) + j.sin(θ)

    # BPSK modulation:
    # Chip = +1 -> transmit carrier normally
    # Chip = –1 -> flip carrier by 180 degrees
    # TODO: implement
    pass



# Quantize to 2-bit signed
# Because FPGA expects signed 2-bit real (I) and im (Q)
# So Python must feed I/Q = {-2, -1, 0, +1}
def quantize_2bit(x):
    # Signal coming in is a float [-1, 1]
    # Rounding and clipping the value outside of range is an option
    # TODO: implement
    pass



# Pack ComplexTimestamp(re(2), im(2), t(12)) -> 16 bits
def pack_complex_timestamp(re2, im2, t12):
    # re2: signed 2-bit
    # im2: signed 2-bit
    # t12: 12-bit unsigned
    # Bit layout (MSB-first): [re1 re0 | im1 im0 | ts11 ts10 ... ts0]

    # Our FPGA uses SInt(2 bits)
    # We need to convert signed Python int to 2-bit hardware int
    # https://docs.python.org/3/reference/datamodel.html#integers

    # Big-endian 16-bit
    # Byte 0 (first) = bits 15..8
    # Byte 1 (second) = bits 7..0
    # TODO: implement
    pass



# AXI-Lite helpers
def axil_write(addr, value):
    """
    AXI-Lite WRITE over UDP -> FPGA (port 1000).

    What this function must do:
      1. Open a UDP socket.
      2. Pack an 8-byte packet:
         - 4 bytes: address (big-endian)
         - 4 bytes: data   (big-endian)
      3. Send packet to (FPGA_IP, PORT_CTRL).
      4. No reply is expected (write = fire-and-forget).

    Examples:
        axil_write(0x00, 1)  → clear reset timeout
        axil_write(0x0C, 0xAA) → set LED pattern
    """
    pass

def axil_read(addr):
    """
    AXI-Lite READ over UDP -> FPGA (port 1000).

    What this function must do:
      1. Open a UDP socket.
      2. Pack a 4-byte packet:
         - 4 bytes: address (big-endian)
      3. Send packet to (FPGA_IP, PORT_CTRL).
      4. Receive a 4-byte reply from FPGA.
      5. Unpack the 32-bit big-endian value and return it.

    Useful registers from EthernetTestbench:
        0x04 → input sample counter
        0x08 → acquisition result counter
        0x10 → FIFO availability (must be checked before sending)
    """
    pass



# UDP sender
# https://docs.python.org/3/howto/sockets.html
def udp_send():
    # AF_INET → IPv4
    # SOCK_DGRAM → UDP
    # Generate baseband signal
    # Sending each sample:
    #   quantize I/Q
    #   Generate 12-bit timestamp
    #   Pack into 16-bit word
    #   Send via UDP
    #   time.sleep(1 µs)
    # TODO: implement
    pass



# UDP receiver
def udp_receive():  
    # Bind to PORT_ACQ
    # Print incoming FPGA acquisition data
    # Parse according to how acquisition module sends results
    # TODO: implement
    pass



# Main
if __name__ == "__main__":
    # Start UDP receiver in background so it can print FPGA results
    # Call udp_send()
    # Keep program alive so the receiver thread doesn't exit
    # TODO: implement
    pass
