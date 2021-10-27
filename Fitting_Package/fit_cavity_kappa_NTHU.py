from scipy import *
import numpy as np
import scipy.interpolate as itp
import matplotlib.pyplot as plt
#import SubtractBackgroundFunc as sbf
# import QubitSpectrumFunc as qsf
from scipy.optimize import curve_fit
import ExtractDataFunc as edf

# DataPath = 'E:/Projects\Fluxonium\data_process/cavity/7.5GHz_5/'
DataPath = 'C:\\Users\\cluster\\Labber\\Data\\2021\\04\\Data_0422\\'
# OneToneFile = 'one tone_tranmon001_94.hdf5'
OneToneFile = 'one tone_transmon001 in 6.55GHz cavity_16.hdf5'

TruncateFreq = False

StartFreq = 6.53 #5.9
EndFreq = 6.58 #5.95

[Freq, Complex] = edf.readFSweepLabber(DataPath + OneToneFile)
print(Freq,
      Complex
      )
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
plt.plot(FreqTrunc, AbsGuess, 'y')
plt.xlabel('freq/GHz', fontsize='x-large')
plt.ylabel('Abs', fontsize='x-large')
plt.tick_params(axis='both', which='major', labelsize='x-large')
plt.title('f0=%.3GGHz, kappa/2pi=%.3GMHz, A=%.3G, B=%.3G' % (f0_fit, kappa_fit * 1e3, A_fit, B_fit))
plt.tight_layout()
plt.show()



