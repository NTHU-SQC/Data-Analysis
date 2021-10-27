import numpy as np
from numpy import pi
import h5py
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

def func(x,a,b,c,d,t1):
    return a * np.cos(b*(x-c)) * np.exp(-(x-c)/t1) - d

directory = 'C:\\Users\\cluster\\Labber\\Data\\2021\\09\\Data_0929'
fname = 'two_tone_EIT_5.94GHz_cavity_test_Rabi_004.hdf5'
path = directory + '\\' + fname

# Read data and plot
with h5py.File(path,'r') as hf:
    print ('Keys of this file: \n', list(hf.keys()))
    data_group = hf['Data']
    print (list(data_group.keys()))
    data = data_group['Data']
    print (data.shape)
    
    # Check logger comment for time duration
    # time duration = flat_time_delta * num of points
    time = np.linspace(0, 200 * 2, data.shape[0])
    
    # Extract I, Q data
    demod_real = data[:,0,0]
    demod_imag = data[:,1,0]
    demod_mag = np.abs(demod_real + 1j*demod_imag) * 1e+6
    demod_phase = np.arctan2(demod_imag, demod_real) * 180/np.pi
    # delay_slope = (demod_phase[-1]-demod_phase[0])/([freq[-1]-freq[0]])
    demod_phase = demod_phase - np.mean(demod_phase)
    demod_phase = np.unwrap(demod_phase)

#plt.plot(time, demod_phase, 'ro-', alpha = 0.5)
plt.plot(time, demod_mag , 'ro-', alpha = 0.5)

# Fitting
"""
guess = ([(np.max(demod_phase)-np.min(demod_phase))*0.5,
           0.5/abs(time[np.argmax(demod_phase)]-time[np.argmin(demod_phase)]),
           time[0],
           demod_phase[0], 1e+4])
"""
guess = ([(np.max(demod_mag)-np.min(demod_mag))*0.5,
           np.pi/abs(time[np.argmax(demod_mag)]-time[np.argmin(demod_mag)]),
           time[0],
           demod_mag[0], 1e+5])

#print(guess)

#opt, cov = curve_fit(func, time, demod_phase, guess)
opt, cov = curve_fit(func, time, demod_mag, guess, maxfev=100000)

err = np.sqrt(abs(np.diag(cov)))

# Pop off specific points => np.delete(array, [idx_list])
time_nice = np.linspace(time[0], time[-1], 201)
plt.plot(time_nice, func(time_nice, *opt) , linewidth = 2.0)
#plt.plot(np.linspace(0,10000,1), func(np.linspace(0,10000,1), *opt))

fitted = func(time_nice, *opt)

pi_pulse      = time_nice[np.argmin(fitted)]
pi_half_pulse = (time_nice[np.argmin(fitted)]+time_nice[np.argmax(fitted)])/2

print(pi_half_pulse - 0.5/opt[1])
if pi_half_pulse - 0.5/opt[1] >= 0:
    if pi_half_pulse - 0.5/opt[1] - int(pi_half_pulse - 0.5/opt[1]) < 0.5:
        pi_half_pulse = int(pi_half_pulse - 0.5/opt[1])
    else:
        pi_half_pulse = int(pi_half_pulse - 0.5/opt[1])+1

fitted_parameter = {'Rabi frequency (MHz)': opt[1]*1e3,
                    'pi pulse (ns)': pi_pulse,
                    'half pi pulse (ns)': pi_half_pulse
                    }
for label,value in fitted_parameter.items():
    print ('{} = {}'.format(label,value))
#print(f"{opt[-1]}")

plt.xlabel('ns')
plt.ylabel('mag ' + '$(\mu v)$')
plt.show()



