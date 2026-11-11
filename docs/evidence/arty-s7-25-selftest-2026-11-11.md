# GpsSelfTest board run

- Date: 2026-11-11T18:05:07-05:00
- Port: COM4, identity 0x47505331, +/-24 coarse bins, 2 emulator channels
- gps-rtl: `b248fee4c5025cffd7b05b09ecda237bb5885ee5 (with uncommitted changes)`
- gps-model: `0d6124f31b70b7ccaf7920abd5456975a8aca62a (with uncommitted changes)`
- fpga-utils: `597e6d59af52254ce40982831fbb6f43359f2f9b (with uncommitted changes)`
- Bitstream: `hw\integration\arty_s7\build\s7-25\gateware\digilent_arty_s7.bit`, SHA-256 `ddb73ce8d69648d69a3633d11361280253f37becade38eab1e7c79046db94705`

Result: **all checks passed**

| Scenario | Status | Satellite | Expected freq / phase | Reported freq / phase / metric | Strongest absent |
| --- | --- | --- | --- | --- | --- |
| baseline: SV 2, +1.0 kHz, phase 37 | PASS | 2 | +8 / 37 | +8 / 37 / 255; +8 / 35 / 136; +8 / 37 / 255 | 18 |
| zero Doppler, zero phase: SV 1 | PASS | 1 | +0 / 0 | +0 / 0 / 255; +0 / 4091 / 255; +0 / 0 / 255 | 15 |
| positive search edge: SV 32, +23.0 kHz | PASS | 32 | +184 / 4091 | +184 / 1 / 188; +184 / 4091 / 255; +184 / 0 / 255 | 15 |
| negative search edge: SV 17, -23.0 kHz | PASS | 17 | -184 / 2046 | -184 / 2047 / 255; -184 / 2046 / 255; -184 / 2044 / 202 | 14 |
| Doppler between fine bins: SV 21, bin 10.5 | PASS | 21 | +10.5 / 500 | +10 / 499 / 185; +10 / 500 / 255; +10 / 502 / 87 | 14 |
| two satellites, equal power: SV 5 and SV 23 | PASS | 5 | +20 / 100 | +20 / 100 / 215; +20 / 101 / 147; +20 / 100 / 223 | 15 |
| two satellites, equal power: SV 5 and SV 23 | PASS | 23 | -60 / 3000 | -60 / 3000 / 173; -60 / 2998 / 94; -60 / 3000 / 184 | 15 |
| two satellites, 12 dB apart, no noise: SV 12 and SV 30 | info | 12 | -33 / 2222 | -33 / 2222 / 255; -33 / 2221 / 255; -33 / 2223 / 255 | 12 |
| two satellites, 12 dB apart, no noise: SV 12 and SV 30 | info | 30 | +77 / 1234 | +77 / 1234 / 32; +77 / 1234 / 31; +77 / 1235 / 25 | 12 |
| code phase 1: SV 9 | PASS | 9 | -12 / 1 | -12 / 2 / 255; -12 / 0 / 255; -12 / 1 / 255 | 15 |
| code phase 818: SV 9 | PASS | 9 | -12 / 818 | -12 / 819 / 255; -12 / 817 / 255; -12 / 819 / 255 | 15 |
| code phase 819: SV 9 | PASS | 9 | -12 / 819 | -12 / 820 / 255; -12 / 821 / 182; -12 / 819 / 255 | 13 |
| code phase 1636: SV 9 | PASS | 9 | -12 / 1636 | -12 / 1636 / 255; -12 / 1637 / 255; -12 / 1636 / 255 | 14 |
| code phase 1637: SV 9 | PASS | 9 | -12 / 1637 | -12 / 1636 / 255; -12 / 1638 / 255; -12 / 1637 / 255 | 15 |
| code phase 2454: SV 9 | PASS | 9 | -12 / 2454 | -12 / 2453 / 255; -12 / 2455 / 255; -12 / 2452 / 182 | 14 |
| code phase 2455: SV 9 | PASS | 9 | -12 / 2455 | -12 / 2454 / 255; -12 / 2456 / 255; -12 / 2454 / 255 | 14 |
| code phase 3273: SV 9 | PASS | 9 | -12 / 3273 | -12 / 3272 / 255; -12 / 3275 / 189; -12 / 3273 / 255 | 16 |
| code phase 3274: SV 9 | PASS | 9 | -12 / 3274 | -12 / 3273 / 255; -12 / 3274 / 255; -12 / 3274 / 255 | 14 |
| code phase 4090: SV 9 | PASS | 9 | -12 / 4090 | -12 / 4091 / 255; -12 / 4090 / 255; -12 / 0 / 182 | 16 |
| noise, about 51 dB-Hz: SV 14 | PASS | 14 | +40 / 1500 | +40 / 1500 / 35; +40 / 1501 / 25; +40 / 1499 / 25 | 5 |
| two satellites in noise, about 57 and 51 dB-Hz: SV 3 and SV 27 | PASS | 3 | -96 / 700 | -96 / 700 / 72; -96 / 700 / 74; -96 / 699 / 50 | 7 |
| two satellites in noise, about 57 and 51 dB-Hz: SV 3 and SV 27 | PASS | 27 | +120 / 3300 | +120 / 3300 / 29; +120 / 3302 / 16; +120 / 3300 / 30 | 7 |
| noise, about 45 dB-Hz: SV 14 | info | 14 | +40 / 1500 | +40 / 1501 / 11; +126 / 3274 / 3; +40 / 1500 / 16 | 4 |
| noise, about 40 dB-Hz: SV 14 | info | 14 | +40 / 1500 | -343 / 1882 / 3; +1673 / 2099 / 3; +513 / 3735 / 3 | 3 |
| noise only, no satellites | info | none | | | 4 |

## Notes and problems

- two satellites, 12 dB apart, no noise: SV 12 and SV 30: satellite 30: metric 32 is not 4x the strongest absent satellite (12)
- two satellites, 12 dB apart, no noise: SV 12 and SV 30: satellite 30: metric 31 is not 4x the strongest absent satellite (12)
- two satellites, 12 dB apart, no noise: SV 12 and SV 30: satellite 30: metric 25 is not 4x the strongest absent satellite (12)
- noise, about 45 dB-Hz: SV 14: satellite 14: metric 11 is not 4x the strongest absent satellite (4)
- noise, about 45 dB-Hz: SV 14: satellite 14: freq_offset 126, expected 40
- noise, about 45 dB-Hz: SV 14: satellite 14: phase_offset 3274, expected 1500
- noise, about 45 dB-Hz: SV 14: satellite 14: metric 3 is below 9
- noise, about 45 dB-Hz: SV 14: satellite 14: metric 3 is not 4x the strongest absent satellite (4)
- noise, about 40 dB-Hz: SV 14: satellite 14: freq_offset -343, expected 40
- noise, about 40 dB-Hz: SV 14: satellite 14: phase_offset 1882, expected 1500
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is below 9
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is not 4x the strongest absent satellite (3)
- noise, about 40 dB-Hz: SV 14: satellite 14: freq_offset 1673, expected 40
- noise, about 40 dB-Hz: SV 14: satellite 14: phase_offset 2099, expected 1500
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is below 9
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is not 4x the strongest absent satellite (3)
- noise, about 40 dB-Hz: SV 14: satellite 14: freq_offset 513, expected 40
- noise, about 40 dB-Hz: SV 14: satellite 14: phase_offset 3735, expected 1500
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is below 9
- noise, about 40 dB-Hz: SV 14: satellite 14: metric 3 is not 4x the strongest absent satellite (3)

Repeatability (10 restarts): PASS, freq/phase values seen: [(-40, 2501), (-40, 2502)]

Soak: PASS, 12544 results in 300 s, 0 bad sweeps, sample overflow clear. Phase error histogram (samples: count) {'-2': 27, '-1': 85, '0': 165, '1': 108, '2': 7}; metric min 134, median 255.
