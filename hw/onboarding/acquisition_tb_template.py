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
PORT_IQ   = 0      # UDP port for IQ samples -> FPGA
PORT_ACQ  = 0      # UDP port for acquisition results <- FPGA

PRN_ID = 1
fs = 1_000_000        
# Chip values = +1/-1 
# Chip sequence = PRN code (1023 chips)
# GPS C/A chip rate = 1.023 MHz    T = 977.5 ns
# 1023 chips x 977.5 ns/chip = 1 ms
# 1 PRN code = 1023 chips = 1 ms long
# Our model expects ~1 sample per chip
    # 4092 chips
    # fs = 1 MHz 
    # 4 ms per PRN cycle

chip_rate = 1_023_000    # GPS C/A
duration_ms = 20         # 20 ms = 20 PRN repetitions
doppler = 4000           # Hz

period = 4092            # Timestamp rollover



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
    
    SV = {
    1: [2, 6],
    2: [3, 7],
    3: [4, 8],
    4: [5, 9],
    5: [1, 9],
    6: [2, 10],
    7: [1, 8],
    8: [2, 9],
    9: [3, 10],
    10: [2, 3],
    11: [3, 4],
    12: [5, 6],
    13: [6, 7],
    14: [7, 8],
    15: [8, 9],
    16: [9, 10],
    17: [1, 4],
    18: [2, 5],
    19: [3, 6],
    20: [4, 7],
    21: [5, 8],
    22: [6, 9],
    23: [1, 3],
    24: [4, 6],
    25: [5, 7],
    26: [6, 8],
    27: [7, 9],
    28: [8, 10],
    29: [1, 6],
    30: [2, 7],
    31: [3, 8],
    32: [4, 9],
}

    tap1, tap2 = SV[prn_id]  
    g1 = 0b1111111111
    g2 = 0b1111111111
    prn = [0]*1023
    
    for i in range(1023):
        feedback1 = ((g1>>2) & 1)^((g1>>9) & 1)
        feedback2 = ((g2>>1) & 1)^((g2>>2) & 1)^((g2>>5) & 1)^((g2>>7) & 1)^((g2>>8) & 1)^((g2>>9) & 1)
        
        prn[i] = ((g1>>9) & 1)^(((g2>>(9-tap1)) & 1)^((g2>>(9-tap2)) & 1))
        g1 = (g1<<1) | (feedback1)
        g2 = (g2<<1) | (feedback2)
        #if prn[i] == 0:
            #prn[i] = 1
        #else:
            #prn[i] = -1
    
    return prn
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
