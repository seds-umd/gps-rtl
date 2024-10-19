tracking

sin/cos gen
* use cordic
* mxu all tracking channels to a single cordic with round robin access
* use parallel cordic arch - highish latency but still gives one output per cycle
* 50 MHz clock, 4.092 MHz sample rate, can fit 12 channels



Modules needed:
* PRN Generator - already done
    * Modify for early, prompt, late codes
* Loop filters - do in software probably
* Carrier generator - CORDIC
* TrackingChannel - single channel
* TrackingControl - controls all the tracking channels


do we need adjustable code period? just change PRN offset instead

do PLLs in software or hardware?

discriminators
code DLL
* 

carrier PLL - costas loop
* I * Q - worst option, harder to implement
* sgn(I) * Q - decent option, easy to implement
* atan(Q/I) - best option, hardest to implement


changes to acquisition
* split incoming samples to acquisition and all tracking channels, stall on all of them
* small fifo (4 or 8 entries) on every sample input (acq and tracking) to improve flow
* consume samples even if it's stalled so it doesn't stall the rest of the samples
* sanity check on fine frequency result - shouldn't be outside a certain range, use this to discard bad results and possibly get better acquisition results

initial version
* inferred muls and divs

nice to have optimizations:
* time multiplexed muls and divs for PLL loop filter and discriminators



phase_bits = 10
period * fine_acq_factor = 2^(fft_len_bits + log2(fine_acq_factor))

inc = (2^phase_bits) * freq * ts
ts = 1 / fs
freq = f_fine_acq * (fs/(period * fine_acq_factor))
inc = (2^phase_bits) * f_fine_acq * / (period * fine_acq_factor)
inc = f_fine_acq >> (fft_len_bits + log2(fine_acq_factor) - phase_bits)


to try next:
* keep bare minimum in tracking channel, move PLLs and discriminators to software and control over ethernet
