# GpsSelfTest board run

- Date: 2026-11-11T19:50:38-05:00
- Port: COM4, identity 0x47505331, +/-24 coarse bins, 2 emulator channels
- gps-rtl: `49df7d354178f4df3eb6df9318fbe3d2a63332c1`
- gps-model: `5bd3049e4bb170b75ed98486c8eaa9478b096975`
- fpga-utils: `268f6f67d0013c5eb96471144a6a07d6179cbc4c`
- Bitstream: `hw\integration\arty_s7\build\s7-25\gateware\digilent_arty_s7.bit`, SHA-256 `f3de8f521918f12793a2a52d67ce5706654571f6db4213d195a726f56da2cedc`

Result: **all checks passed**

| Scenario | Status | Satellite | Expected freq / phase | Reported freq / phase / metric | Strongest absent |
| --- | --- | --- | --- | --- | --- |
| baseline: SV 2, +1.0 kHz, phase 37 | PASS | 2 | +8 / 37 | +8 / 37 / 255; +8 / 37 / 255; +8 / 37 / 255 | 16 |
| zero Doppler, zero phase: SV 1 | PASS | 1 | +0 / 0 | +0 / 0 / 255; +0 / 0 / 255; +0 / 0 / 255 | 16 |
| outermost positive search bin: SV 6, +24.0 kHz | PASS | 6 | +192 / 3000 | +192 / 3000 / 255; +192 / 3000 / 255; +192 / 3000 / 255 | 15 |
| outermost negative search bin: SV 26, -24.0 kHz | PASS | 26 | -192 / 1000 | -192 / 1000 / 255; -192 / 1000 / 255; -192 / 1000 / 255 | 16 |
| one bin inside the positive edge: SV 32, +23.0 kHz | PASS | 32 | +184 / 4091 | +184 / 4091 / 255; +184 / 4090 / 255; +184 / 4091 / 255 | 14 |
| one bin inside the negative edge: SV 17, -23.0 kHz | PASS | 17 | -184 / 2046 | -184 / 2046 / 255; -184 / 2046 / 255; -184 / 2046 / 255 | 15 |
| Doppler between fine bins: SV 21, bin 10.5 | PASS | 21 | +10.5 / 500 | +11 / 500 / 255; +10 / 499 / 182; +10 / 500 / 255 | 13 |
| two satellites, equal power: SV 5 and SV 23 | PASS | 5 | +20 / 100 | +20 / 100 / 220; +20 / 100 / 212; +20 / 100 / 214 | 15 |
| two satellites, equal power: SV 5 and SV 23 | PASS | 23 | -60 / 3000 | -60 / 3000 / 185; -60 / 3000 / 183; -60 / 3000 / 185 | 15 |
| two satellites, 12 dB apart, no noise: SV 12 and SV 30 | info | 12 | -33 / 2222 | -33 / 2222 / 255; -33 / 2222 / 255; -33 / 2222 / 255 | 14 |
| two satellites, 12 dB apart, no noise: SV 12 and SV 30 | info | 30 | +77 / 1234 | +77 / 1234 / 31; +77 / 1234 / 31; +77 / 1234 / 29 | 14 |
| code phase 1: SV 9 | PASS | 9 | -12 / 1 | -12 / 1 / 255; -12 / 1 / 255; -12 / 1 / 255 | 16 |
| code phase 511: SV 9 | PASS | 9 | -12 / 511 | -12 / 511 / 255; -12 / 511 / 255; -12 / 511 / 255 | 16 |
| code phase 512: SV 9 | PASS | 9 | -12 / 512 | -12 / 512 / 255; -12 / 512 / 255; -12 / 512 / 255 | 14 |
| code phase 1023: SV 9 | PASS | 9 | -12 / 1023 | -12 / 1023 / 255; -12 / 1023 / 255; -12 / 1023 / 255 | 15 |
| code phase 1024: SV 9 | PASS | 9 | -12 / 1024 | -12 / 1024 / 255; -12 / 1024 / 255; -12 / 1024 / 255 | 15 |
| code phase 2046: SV 9 | PASS | 9 | -12 / 2046 | -12 / 2046 / 255; -12 / 2046 / 255; -12 / 2046 / 255 | 14 |
| code phase 2047: SV 9 | PASS | 9 | -12 / 2047 | -12 / 2047 / 255; -12 / 2047 / 255; -12 / 2047 / 255 | 15 |
| code phase 3069: SV 9 | PASS | 9 | -12 / 3069 | -12 / 3069 / 255; -12 / 3069 / 255; -12 / 3069 / 255 | 16 |
| code phase 3070: SV 9 | PASS | 9 | -12 / 3070 | -12 / 3070 / 255; -12 / 3070 / 255; -12 / 3070 / 255 | 16 |
| code phase 4090: SV 9 | PASS | 9 | -12 / 4090 | -12 / 4090 / 255; -12 / 4090 / 255; -12 / 4090 / 255 | 14 |
| noise, about 51 dB-Hz: SV 14 | PASS | 14 | +40 / 1500 | +40 / 1500 / 34; +40 / 1500 / 36; +40 / 1500 / 36 | 4 |
| two satellites in noise, about 57 and 51 dB-Hz: SV 3 and SV 27 | PASS | 3 | -96 / 700 | -96 / 700 / 68; -96 / 700 / 72; -96 / 700 / 69 | 6 |
| two satellites in noise, about 57 and 51 dB-Hz: SV 3 and SV 27 | PASS | 27 | +120 / 3300 | +120 / 3300 / 28; +120 / 3300 / 32; +120 / 3300 / 31 | 6 |
| noise, about 45 dB-Hz: SV 14 | info | 14 | +40 / 1500 | +40 / 1500 / 16; +40 / 1500 / 18; +40 / 1500 / 16 | 3 |
| noise, about 40 dB-Hz: SV 14 | info | 14 | +40 / 1500 | -1409 / 2903 / 3; -1099 / 1599 / 4; -1715 / 1793 / 3 | 4 |
| noise only, no satellites | PASS | none | | | 4 |

## Notes and problems

- two satellites, 12 dB apart, no noise: SV 12 and SV 30: satellite 30: metric 31 is not 4x the strongest absent satellite (14)
- two satellites, 12 dB apart, no noise: SV 12 and SV 30: satellite 30: metric 31 is not 4x the strongest absent satellite (14)
- two satellites, 12 dB apart, no noise: SV 12 and SV 30: satellite 30: metric 29 is not 4x the strongest absent satellite (14)
- noise, about 40 dB-Hz: SV 14: satellite 14: freq_offset -1409, expected 40
- noise, about 40 dB-Hz: SV 14: satellite 14: phase_offset 2903, expected 1500
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is below 9
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is not 4x the strongest absent satellite (4)
- noise, about 40 dB-Hz: SV 14: satellite 14: freq_offset -1099, expected 40
- noise, about 40 dB-Hz: SV 14: satellite 14: phase_offset 1599, expected 1500
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 4 is below 9
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 4 is not 4x the strongest absent satellite (4)
- noise, about 40 dB-Hz: SV 14: satellite 14: freq_offset -1715, expected 40
- noise, about 40 dB-Hz: SV 14: satellite 14: phase_offset 1793, expected 1500
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is below 9
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is not 4x the strongest absent satellite (4)

Repeatability (10 restarts): PASS, freq/phase values seen: [(-40, 2500)]

Soak: PASS, 12544 results in 300 s, 0 bad sweeps, sample overflow clear. Phase error histogram (samples: count) {'-1': 4, '0': 388}; metric min 255, median 255.
