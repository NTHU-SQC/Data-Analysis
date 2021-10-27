# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:52:10 2021

@author: cluster
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import numpy as np
import h5py
import Labber
import datetime


DataPath = 'C:\\Users\\cluster\\Labber\\Data\\2021\\07\\Data_0707\\'
OneToneFile = 'one tone_3DtransmonTwoQ001_sweep power_002.hdf5'
ATS_var = 'Alazar - Channel A - Average demodulated value'
BackFreq_var = 'Qubit - Frequency'

file = DataPath + OneToneFile
LogData = Labber.LogFile(file)
Entries = LogData.getEntry()

TruncateFreq = False
StartFreq = 6.53
EndFreq = 6.58

if BackFreq_var not in Entries:
    BackFreq_var =  'RF_ReadOut2 - Frequency'  #'Readout - Frequency'   ###change name based on hardware
BackComplex = np.conj(LogData.getData(ATS_var)[-1]) # idx 7 for sweep power002 => -21dBm
BackFreq = LogData.getData(BackFreq_var)[0] * 1e-9 #

[Freq, Complex]= [BackFreq, BackComplex]  #[Freq, Complex] = edf.readFSweepLabber(DataPath + OneToneFile)
###########edf read data


# [Freq, Complex] = edf.readVNAS21(DataPath + OneToneFile)
# Complex = np.sqrt(Complex)
Complex = Complex ** 2
if TruncateFreq:
    FreqInd = (EndFreq >= Freq) == (Freq >= StartFreq)
    FreqTrunc = Freq[FreqInd]
    ComplexTrunc = Complex[FreqInd]
else:
    FreqTrunc = Freq
    ComplexTrunc = Complex

AbsComplex = np.abs(ComplexTrunc)
MaxAbs = np.max(AbsComplex)
ComplexTrunc /= MaxAbs
AbsComplex = np.abs(ComplexTrunc)
MaxAbs = np.max(AbsComplex)
MinAbs = np.min(AbsComplex)
MaxInd = AbsComplex.argmax()
f0_guess = FreqTrunc[MaxInd]
kappa_guess = (FreqTrunc[-1] - FreqTrunc[0]) / 4
B_guess = MinAbs
A_guess = (MaxAbs - MinAbs) * (kappa_guess / 2) ** 2


def lorenztian(f, f0, kappa, A, B):
    t = A / ((f - f0) ** 2 + (kappa / 2) ** 2) + B
    return t


guess = ([f0_guess, kappa_guess, A_guess, B_guess])
bounds = (
    (Freq[0], 0, 0, 0),
    (Freq[-1], kappa_guess * 4, MaxAbs * 10, MaxAbs)
)

qopt, qcov = curve_fit(lorenztian, FreqTrunc, AbsComplex, guess, bounds=bounds)
f0_fit, kappa_fit, A_fit, B_fit = qopt
kappa_fit = np.abs(kappa_fit)

AbsGuess = lorenztian(FreqTrunc, f0_guess, kappa_guess, A_guess, B_guess)
AbsFit = lorenztian(FreqTrunc, f0_fit, kappa_fit, A_fit, B_fit)
print('f0=%.5GGHz, kappa/2pi=%.3GMHz, A=%.3G, B=%.3G' % (f0_guess, kappa_guess * 1e3, MaxAbs, MinAbs))

fig, ax = plt.subplots()
leg = ()
plt.plot(FreqTrunc, AbsComplex, '.')
plt.plot(FreqTrunc, AbsFit, 'r')
#plt.plot(FreqTrunc, AbsGuess, 'y')
plt.xlabel('freq/GHz', fontsize='x-large')
plt.ylabel('Abs', fontsize='x-large')
plt.tick_params(axis='both', which='major', labelsize='x-large')
plt.title('f0=%.5GGHz, kappa/2pi=%.3GMHz, A=%.3G, B=%.3G' % (f0_fit, kappa_fit * 1e3, A_fit, B_fit))
plt.tight_layout()
plt.show()
