import numpy as np
import h5py
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from textwrap import wrap

def func(x, a, b, c, d):
    return a*np.exp(-(x-c)/b) + d

directory = 'C:\\Users\\cluster\\Labber\\Data\\2021\\04\\Data_0422'
fname = 'two tone_tranmon001 in 6.55GHz cavity_T2_echo_19.hdf5'
path = directory + '\\' + fname
t2_guess = 10e3

#Read data and fit
with h5py.File(path,'r') as hf:
    print('List of arrays in this file: \n', list(hf.keys()))
    data_group = hf['Traces']
    # print (list(data_group.keys()))
    #channel_names = data_group['Channel names']
    # print (channel_names[0:])
    data = data_group['Alazar - Channel A - Average buffer demodulated values']
    print (data.shape)
    time = np.linspace(0, 100 * 150, 151)
    #time = data[:,0,0]
    demod_real = data[:,0,0]
    demod_imag = data[:,1,0]
    demod_mag = np.absolute(demod_real+1j*demod_imag)
    demod_phase = np.arctan2(demod_imag,demod_real)*180/np.pi
# =============================================================================
#     for index in range(len(demod_phase)):
#         if demod_phase[index] <= 0:
#             demod_phase[index] = demod_phase[index] + 360
# =============================================================================
            
    #print (demod_phase)
    demod_phase = demod_phase - np.min(demod_phase)

# demod_phase = demod_mag
plt.plot(time*1e-3, demod_phase, '-d', alpha = 0.5)

guess = ([demod_phase[0]-demod_phase[-1], t2_guess, 0, demod_phase[-1]])
popt, pcov = curve_fit(func, time, demod_phase, guess)
perr = np.sqrt(abs(np.diag(pcov)))
time_nice = np.linspace(time[0], time[-1], 100)
plt.plot(time_nice*1e-3,func(time_nice, *popt), linewidth = 2.0)
plt.title('{} +/- {}'.format(popt[1]*1e-3, perr[1]*1e-3))
plt.xlabel('us')
plt.ylabel('degree')
plt.show()