# Modular Acquisition Design

FFT inputs:
* GPS samples (for, acq)
* PRN samples (for, acq)
* Mixed GPS/PRN samples (rev, acq)
* Decimated samples (for, fine)

FFT outputs:
* Conjugate (acq)
* Freq shift/roll (acq)
* Mag (acq)
* Mag (fine)

Mag inputs:
* FFT (acq)
* FFT (fine)

Mag outputs:
* Max (acq)
* Max (fine)


Input - stream




## FSM

Get samples
* FFT in from GPS
* FFT out to sample memory
* Go to get PRN

Get PRN
* FFT in from PRN generator
* FFT out to PRN memory
* Go to mix
