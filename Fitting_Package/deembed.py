# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 18:31:23 2021

@author: Alaster
"""

import os.path
import numpy as np
from hdf5Reader import get_hdf5_path, formatConvert, selectFromList, \
    open_hdf5, add_to_hdf5, copy_hdf5


def interface(file: str = '', file_BG: str = ''):
    """
    Load hdf5 file directories for both data & background data.

    Parameters
    ----------
    file : str, optional
        File directory for data. The default is ''.
    file_BG : str, optional
        File directory for background data. The default is ''.

    Returns
    -------
    file : str
        Same as above.
    file_BG : str
        Same as above.

    """
    # loop until none empty file name is selected
    while file == '':
        file = get_hdf5_path(title='Import data to be deembeded')
        if file:
            _, name = os.path.split(file)
            print('file selected: ' + name)

    # if BG name is empty, the BG name will be the same as previous file name
    if file_BG == '':
        file_BG = get_hdf5_path(
            title='Import BG data, data to be deembeded=>' + name)
        if not file_BG:
            file_BG = file
        _, name = os.path.split(file_BG)
        print('file selected: ' + name)
    return file, file_BG


def _preprocess(data: str, namelist: list, selected_axisname: str = None):
    # keep original shape
    original_shape = data.shape

    # select deembed axis, use the input 'selected_axisname' if specified
    namelist_app = ['x-axis'] + namelist
    if not selected_axisname:
        axisIdx = selectFromList(
            namelist_app, 'Select deembed axis', True
            )
        selected_axisname = namelist_app[axisIdx]
    else:
        axisIdx = namelist_app.index(selected_axisname)

    # transpose & reshape
    data = np.moveaxis(data, axisIdx, 0)
    transposed_shape = data.shape  # keep transposed shape
    data = np.reshape(data, [data.shape[0], np.prod(data.shape[1:])], 'F')
    return data, original_shape, selected_axisname, axisIdx, transposed_shape


def _postprocess(data: np.array, transposed_shape: tuple,
                 axisIdx: int, original_shape: tuple):
    temp = np.reshape(data, transposed_shape, 'F')
    temp = np.moveaxis(temp, axisIdx, 0)
    return formatConvert(np.reshape(temp, original_shape, 'F'))


def deembedVNA(file: str, file_BG: str, header: str = 'Normalized_'):
    """
    De-embed VNA hdf5 data.

    Parameters
    ----------
    file : str
        File directory for data.
    file_BG : str
        File directory for background data.
    header : str, optional
        Prefix for newly generated file. The default is 'Normalized_'.

    """
    # read and preprocess data
    *a, log_channel = open_hdf5(file)[2:5]
    data, ori_shape, selected, axisIdx, tp_shape = _preprocess(*a)
    data_BG = _preprocess(*open_hdf5(file_BG)[2:4], selected)[0]

    # average over 'data_BG' if 'data_BG' is not of the same shape with 'data'
    if data_BG.shape != data.shape:
        data_BG = np.mean(data_BG, axis=1)[:, np.newaxis]

    # remove background, restore format then save
    data /= data_BG
    temp = _postprocess(data, tp_shape, axisIdx, ori_shape)
    # save_to_copy_hdf5(temp, log_channel, file, prefix=header)
    sv = copy_hdf5(file, prefix=header)
    add_to_hdf5(temp, log_channel + '_deembed', sv, unit='')


def deembedDigitizer(
        file: str, file_BG: str, header: str = 'Normalized_', mode: str = 'all'
        ):
    """
    De-embed Digitizer hdf5 data.

    Parameters
    ----------
    file : str
        File directory for data.
    file_BG : str
        File directory for background data.
    header : str, optional
        Prefix for newly generated file. The default is 'Normalized_'.
    mode : str, optional
        Choose de-embed mode, 'sub' for subtraction, 'div' for division. The
        default is 'all' for both.

    """
    *a, log_channel = open_hdf5(file)[2:5]
    data, ori_shape, selected, axisIdx, tp_shape = _preprocess(*a)
    data_BG = _preprocess(*open_hdf5(file_BG)[2:4], selected)[0]

    # average over 'data_BG' if 'data_BG' is not of the same shape with 'data'
    if data_BG.shape != data.shape:
        data_BG = np.mean(data_BG, axis=1)[:, np.newaxis]

    # remove background, restore format then save
    sv = copy_hdf5(file, prefix=header)
    if mode == 'all' or mode == 'sub':
        V_sub = (abs(data) - abs(data_BG)) * np.exp(1j * np.angle(data))
        temp = _postprocess(V_sub, tp_shape, axisIdx, ori_shape)
        add_to_hdf5(temp, log_channel + '_deembed_sub', sv)

    if mode == 'all' or mode == 'div':
        V_div = data / data_BG
        temp = _postprocess(V_div, tp_shape, axisIdx, ori_shape)
        add_to_hdf5(temp, log_channel + '_deembed_div', sv, unit='')


if __name__ == '__main__':
    # file, file_BG = interface()
    # deembedVNA(file, file_BG)
    # deembedDigitizer(file, file_BG)
    pass
