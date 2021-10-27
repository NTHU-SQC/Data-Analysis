#import pyautogui as auto
#import time
import numpy as np
import h5py
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from textwrap import wrap

## new data structure (data structure without trace)

def func(x,a,b,c,d,t2):
    return a*np.cos(2*np.pi*b*(x-c))*np.exp(-(x-c)/t2) - d

directory = 'C:\\Users\\cluster\\Labber\\Data\\2021\\07\\Data_0713'
fname = 'AdTr_two tone_tranmon001 in 6.55GHz cavity_AdTr_Ramsey_026.hdf5'


path = directory + '\\' + fname

#Read data and fit
'''
with h5py.File(path,'r') as hf:
    print('List of arrays in this file: \n', list(hf.keys()))
    data_group = hf['Data']
    #print (list(data_group.keys()))
    data_group_2 = hf['Data']['Data']
    data_group_3 = np.array(data_group_2)
    x = data_group_3[:,0,0] * 1e+6 #real
    y = data_group_3[:,1,0] * 1e+6 #imag
    
#plt.plot(x,y)
#plt.show()
'''

t2_guess = 10000
#Read data and fit
with h5py.File(path,'r') as hf:
    print('List of arrays in this file: \n', list(hf.keys()))
    data_group = hf['Data']
    #print (list(data_group.keys()))
    data_group_2 = hf['Data']['Data']
    data_group_3 = np.array(data_group_2)
    time = np.linspace(0,20*600,600)  
    #(0,7500,151)  #wfm_amount = 600*qubitDrive_delay_time_delta =20
#   time = data[:,0,0]
    demod_real = data_group_3[:,0,0] #* 1e+6 #real
    demod_imag = data_group_3[:,1,0] #* 1e+6 #imag
    demod_mag = np.absolute(demod_real+1j*demod_imag)
    demod_phase = np.arctan2(demod_imag,demod_real)*180/np.pi
    
    for index in range(len(demod_phase)):
        if demod_phase[index] <= 0:
            demod_phase[index] = demod_phase[index] + 360
            
    #print (demod_phase)
    #demod_phase = demod_phase - np.min(demod_phase)

plt.figure(figsize=(8,8))
plt.plot(time*1e-3, demod_phase, 'r-o', alpha = 0.5, label="exp_data")


####################################################################################################

guess = ([(np.max(demod_phase)-np.min(demod_phase))*0.5, 0.5/abs(time[np.argmax(demod_phase)]-time[np.argmin(demod_phase)]), time[0], demod_phase[0], t2_guess])
opt,cov = curve_fit(func, time, demod_phase, guess)
err = np.sqrt(abs(np.diag(cov)))
time_nice = np.linspace(time[0], time[-1], 100)
plt.plot(time_nice*1e-3, func(time_nice, *opt), linewidth = 2.0, label="fit")

t2_fit = opt[-1]
fitted_parameter = {'Ramsey frequency (MHz)': opt[1]*1e-6,
                    'T2 Ramsey (us)': t2_fit*1e-3
                    }
for label,value in fitted_parameter.items():
    print ('{} = {}'.format(label,value))

plt.legend()
plt.xlabel('us')
plt.ylabel('degree')
plt.show()