# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 13:07:32 2021

Find n-smallest/largest elements in an array
    https://stackoverflow.com/questions/31642353/

@author: Alaster
"""

from circuit import reflection_port
from hdf5Reader import get_VNA_Data, get_hdf5_path, contour, valueSelection
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from numbers import Number


def dBmSelect(dBm, yname, dBm_select=None, qText='Select case from below'):
    yunit = yname.split('(')[1].replace(')', '')
    yname = yname.split('(')[0]

    if dBm_select and isinstance(dBm_select, Number):
        dBm_index = (np.abs(dBm - dBm_select)).argmin()
    else:
        dBm_index = valueSelection(dBm, yname, yunit, qText)
    return dBm_index


def relaxfit(freq, dBm, S21, yname, dBm_select=None, show=True):
    # slicing data
    dBm_index = dBmSelect(
        dBm, yname, dBm_select=None, qText='Select low power case:'
        )

    # circle-fit data
    obj = reflection_port(freq, S21[:, dBm_index])
    obj.autofit()

    # extract equvalent relaxation and decoherence rates
    fr, Ql, absQc = obj.fr, obj.Ql, obj.absQc
    relax = fr / absQc
    decoh = fr / (2 * Ql)
    dephase = decoh - relax/2

    if show:
        # plot
        obj.plotall()
        print(f"fit power level: {dBm[dBm_index]} dBm\n" +
              f"resonant freq: {fr/1e6} MHz\n" +
              f"relaxation rate: {relax/1e6} MHz\n" +
              f"decoherence rate: {decoh/1e6} MHz\n" +
              f"pure dephasing rate: {dephase/1e6} MHz\n" +
              f"relax/decoh: {relax/decoh}")
    return relax, decoh, dephase


def powerfit(dBm, S21, xname, yname, zname, relax, decoh, dBm_select=None,
             attenuation_dB=0, vpScale=False, show=True):
    # slicing data
    contour(x, y, z, xname, yname, zname)
    dBm_index = dBmSelect(dBm, yname, dBm_select=None,
                          qText='Enter hi-SNR row value to extract fr:')
    f_idx = np.abs(S21[:, dBm_index]).argmin()
    S21Mag = np.abs(S21[f_idx, :])

    # set x scale
    if vpScale:
        def convfun(dBm):
            return dBm2vp(dBm)
        unit = 'Vp'
    else:
        def convfun(dBm):
            return np.sqrt(dBm2p(dBm))
        unit = 'sqrt(W)'

    gamma = relax / decoh

    def r(dBm, ke):
        omega = ke * convfun(dBm - attenuation_dB)
        Omega = omega/decoh
        return np.abs(1 - gamma / (1 + Omega ** 2 / gamma))

    # initial guess min r
    if gamma >= 1:  # using root when it exist
        rabi0 = np.sqrt(gamma * (gamma - 1)) * decoh
        ke0 = rabi0 / convfun(dBm[S21Mag.argmin()] - attenuation_dB)
    else:
        # if not, use the fact that mid-high magnitude at rabi=sqrt(gamma)
        rabi_hp = np.sqrt(gamma) * decoh
        # use 5 smallest elements to determine minimum
        S21_hp = (np.mean(np.partition(S21Mag, 5)[:5]) + 1) / 2
        ke0 = rabi_hp / convfun(
            dBm[np.abs(S21Mag - S21_hp).argmin()] - attenuation_dB
            )
        # ke0 = 1e9 * 10**(attenuation_dB/20)

    # curve fit
    popt, pcov = curve_fit(r, dBm, S21Mag, p0=ke0, bounds=(0, np.inf),)
    ke = popt[0]

    if show:
        # plot
        plt.plot(dBm, S21Mag, 's-', label='data')
        plt.plot(dBm, r(dBm, ke), 'r', label='fit')
        plt.xlabel('Power (dBm)')
        plt.ylabel('S21 Magnitude')
        plt.legend()
        plt.show()

        comment = 'chip level'
        if attenuation_dB == 0:
            comment = 'not ' + comment
        val = '{:.6e}'.format(ke/1e6)
        print(f"k: {val} MHz/" + unit + " (" + comment + ')')
    return ke


def p2dBm(p):  # W to dBm
    return 10 * np.log10(p / 1e-3)


def vp2p(vp, Z0=50):  # Vp to W
    return vp**2 / 2 / Z0


def vp2dBm(vp, Z0=50):  # Vp to dBm
    return p2dBm(vp2p(vp, Z0))


def dBm2p(dBm):  # dBm to W
    return 1e-3 * 10 ** (dBm/10)


def p2vp(p, Z0=50):  # W to Vp
    return np.sqrt(2 * Z0 * p)


def dBm2vp(dBm, Z0=50):  # dBm to Vp
    return p2vp(dBm2p(dBm), Z0)


if __name__ == '__main__':
    x, y, z, xname, yname, zname = get_VNA_Data(get_hdf5_path())
    relax, decoh, dephase = relaxfit(x, y, z, yname)
    ke = powerfit(y, z, xname, yname, zname, relax, decoh, attenuation_dB=125)
