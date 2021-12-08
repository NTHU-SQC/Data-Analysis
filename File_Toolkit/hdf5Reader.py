# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 15:52:32 2021

@author: Alaster
"""

import numpy as np
import tkinter
from tkinter import filedialog
import h5py
from collections import Counter
import matplotlib.pyplot as plt
import os.path
from shutil import copyfile


def get_hdf5_path(title: str = 'Select item'):
    """
    Interactive dialogue box to get hdf5 file.

    Parameters
    ----------
    title : str, optional
        Title of the dialogue box. The default is 'Select item'.

    Returns
    -------
    str
        Path string.

    """
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return filedialog.askopenfilename(
        filetypes=[('.HDF Files', '.hdf5')],
        title=title)


def plot(x: np.array, y: np.array, z: np.array,
         xname: str = 'xname', yname: str = 'yname', zname: str = 'zname'):
    """
    Plotting Interface. The default is 2D-plot if y-axis has only 1
    entry, otherwise auto-switch to contour plot.

    Parameters
    ----------
    x : np.array
        x-axis array.
    y : np.array
        y-axis array.
    z : np.array
        z-axis mesh array.
    xname : str, optional
        x-axis title. The default is 'xname'.
    yname : str, optional
        y-axis title. The default is 'yname'.
    zname : str, optional
        z-axis title. The default is 'zname'.

    """
    if len(y) > 1:
        contour(x, y, z, xname, yname, zname)
        return
    fig, ax = plt.subplots()
    ax.set_title(yname + ' = ' + str(y[0]))
    ax.plot(x, np.abs(z), 'b')
    ax.set_xlabel(xname)
    ax.set_ylabel(zname + ' Magnitude', color="blue")
    ax2 = ax.twinx()
    ax2.plot(x, np.angle(z, True), 'r')
    ax2.set_ylabel(zname + ' Phase (deg)', color="red")


def contour(x: np.array, y: np.array, z: np.array,
            xname: str = 'xname', yname: str = 'yname', zname: str = 'zname'):
    """
    Plotting contour map.

    Parameters
    ----------
    x : np.array
        x-axis array.
    y : np.array
        y-axis array.
    z : np.array
        z-axis mesh array.
    xname : str, optional
        x-axis title. The default is 'xname'.
    yname : str, optional
        y-axis title. The default is 'yname'.
    zname : str, optional
        z-axis title. The default is 'zname'.

    """
    if np.iscomplexobj(z):
        z = np.abs(z)
    a = plt.pcolormesh(*np.meshgrid(x, y), z.transpose(), shading='auto')
    plt.xlabel(xname)
    plt.ylabel(yname)
    b = plt.colorbar(a)
    b.ax.set_ylabel(zname)
    plt.show()


def zoom(x: np.array, y: np.array, z: np.array,
         xRange: tuple = (-np.inf, np.inf), yRange: tuple = (-np.inf, np.inf)):
    """
    Return zoomed x, y, z arrays.

    Parameters
    ----------
    x : np.array
        x-axis array.
    y : np.array
        y-axis array.
    z : np.array
        z-axis mesh array.
    xRange : tuple, optional
        Range values for x-axis. The default is (-np.inf, np.inf).
    yRange : tuple, optional
        Range values for y-axis. The default is (-np.inf, np.inf).

    Returns
    -------
    x_zoom : np.array
        zoomed x-axis.
    y_zoom : np.array
        zoomed y-axis.
    z_zoom : np.array
        zoomed z-axis.

    """
    # zoom x
    index_bool = x <= xRange[1]
    x_zoom, z_zoom = x[index_bool], z[index_bool, :]
    index_bool = x_zoom >= xRange[0]
    x_zoom, z_zoom = x_zoom[index_bool], z_zoom[index_bool, :]

    # zoom y
    index_bool = y <= yRange[1]
    y_zoom, z_zoom = y[index_bool], z_zoom[:, index_bool]
    index_bool = y_zoom >= yRange[0]
    y_zoom, z_zoom = y_zoom[index_bool], z_zoom[:, index_bool]
    return x_zoom, y_zoom, z_zoom


def selectFromList(listItem: list, qText: str = '',
                   returnIndex: bool = False, allOption: bool = False):
    """
    Return the selected object or index from a list.

    Parameters
    ----------
    listItem : list
        List of objects.
    qText : str, optional
        Dialogue text. The default is ''.
    returnIndex : bool, optional
        Set True to return index, otherwise selected item from the list. The
        default is False.
    allOption : bool, optional
        Set True to enable 'all' selection keyword ':'. Enter non-int text
        after the dialogue text to trigger all item output. The default is
        False.

    """
    itemString = ''
    for i, j in enumerate(listItem):
        itemString += str(i) + ': ' + str(j) + '\n'
    try:
        val = input(qText + ':\n' + itemString + '=>')
        idx = int(val)
    except(TypeError):
        if allOption:
            return ':'
        raise ValueError(
            'The input field must be an integer unless allOption is enabled'
            )
    if returnIndex:
        return idx
    return listItem[idx]


def formatConvert(z: np.array, yshape: list = []):
    """
    Conversion between Labber format and common Fortran type array shape. Empty
    yshape argument leads to conversion to Labber format or inverted operation
    otherwise.

    Parameters
    ----------
    z : np.array
        z-axis data to be converted.
    yshape : list, optional
        Shape data for the final output. The default is [].

    Returns
    -------
    np.array
        Transformed z-axis.

    """
    if yshape:  # Labber hdf5 format to normal format
        ztemp = z[:, 0, :]
        if z.shape[1] > 1:
            ztemp = ztemp + 1j * z[:, 1, :]
        return np.reshape(ztemp, [ztemp.shape[0]] + list(yshape), 'F')

    # normal format to Labber hdf5 format
    if np.iscomplexobj(z):
        ztemp = np.reshape(z, [z.shape[0], np.prod(z.shape[1:])], 'F')
        ztemp = np.stack((np.real(ztemp), np.imag(ztemp)), axis=1)
    else:
        ztemp = np.reshape(z, [z.shape[0], 1, np.prod(z.shape[1:])], 'F')
    return ztemp


def valueSelection(axis: np.array, name: str, unit: str,
                   qText: str = 'Select case from below'):
    """
    Select a value from an array. This function returns index corresponds to
    the value closest to the input from the given array.

    Parameters
    ----------
    axis : np.array
        Array used to select value.
    name : str
        Name of the array.
    unit : str
        Unit of the array data.
    qText : str, optional
        Descirption of the array. The default is 'Select case from below'.

    Returns
    -------
    idx : int
        Selected index.

    """
    print('\n' + qText)
    print('Axis name: ' + name + ' (' + unit + ')')
    step = axis[1] - axis[0] if len(axis) > 1 else 0
    print(
        f'max= {max(axis)}, min: {min(axis)}, step: ' + '{:.4e}'.format(step)
        )
    flag = True
    while flag:
        val = input(f'Enter value {unit}=>')
        try:
            val = float(val)
            flag = False
        except ValueError:
            continue
    idx = (np.abs(axis - val)).argmin()
    return idx


def _selectyaxis(axisList, namelist, unitlist):
    flag = selectFromList(namelist, 'Select output y-axis', True, True)
    if isinstance(flag, str):   # select all axis as output
        dimList = [range(len(item)) for item in axisList]
        return axisList, namelist, unitlist, dimList
    dimList = []
    for i, (axis, name, unit) in enumerate(zip(axisList, namelist, unitlist)):
        if i == flag:   # range all value for selected y axis
            dimList += [range(len(axis))]
            continue
        idx = valueSelection(axis, name, unit)
        dimList += [idx]
    return axisList[flag], namelist[flag], unitlist[flag], dimList


def _meshSlice(zMesh, yaxisList, ynamelist, yunitlist):
    if len(ynamelist) > 1:
        y, yname, yunit, dimList = _selectyaxis(
            yaxisList, ynamelist, yunitlist
            )
        temp = np.moveaxis(zMesh, 0, -1)[tuple(dimList)]
        z = np.moveaxis(temp, -1, 0)
    else:
        y, yname, yunit = yaxisList[0], ynamelist[0], yunitlist[0]
        z = zMesh
    return z, y, yname, yunit


def _sort_Data_ys(f, ylist_idx=None):
    nameList, axisList, dimList = [], [], []

    # return empty dict and list if nothing is in 'Channel names'
    if len(f['Data/Channel names'][:]) == 0:
        return [''], [np.array([0])], [1]

    # use total points to estimate number of indepedent variables
    def_name = f['Log list'][0][0]
    total_DOF = len(f['Traces'][def_name][0, 0, :])
    i = 0
    while total_DOF != 1:  # escape if num of independent variable is reached
        nameList += [f['Data/Channel names'][:][i][0]]
        val = f['Data/Data'][:, i, :]
        if i == 0:  # mainloop
            axisList += [val[:, 0]]
        else:   # other layer of loops
            axisList += [np.sort(list(Counter(val[0, :]).keys()))]
        dimVal = len(axisList[i])
        dimList += [dimVal]
        total_DOF //= dimVal
        i += 1
    return nameList, axisList, dimList


def _sort_Traces_xz(f, log_ch_idx=None, yshape=[]):
    if not log_ch_idx:
        if len(f['Log list']) == 1:
            log_ch_idx = 0
        else:
            namelist = [f['Log list'][i][0] for i in range(len(f['Log list']))]
            log_ch_idx = selectFromList(
                namelist, 'Choose the log channel index from below', True
                )
    log_name = f['Log list'][log_ch_idx][0]
    data = f['Traces']
    t0, dt = data[log_name + '_t0dt'][:][0, :]
    N = data[log_name + '_N'][:][0]
    x = t0 + dt * np.linspace(0, N, N+1)[:-1]
    z = formatConvert(data[log_name], yshape)
    return x, z, log_name


def _get_unit(f, channel_name, returnIdx=False):
    data = f['Channels']
    idx = [data[i][0] for i in range(len(data))].index(channel_name)
    unit = data[idx][3]
    if returnIdx:
        return idx
    return unit


# Interfaces
def open_hdf5(file: str = None, log_ch_idx: int = 0):
    """
    Open and extract Labber-formatted hdf5 file.

    Parameters
    ----------
    file : str, optional
        Path string of the hdf5 file. The default is None.
    log_ch_idx : int, optional
        Log channel index. This depends on the Labber measurement file setting.
        The default is 0.

    Returns
    -------
    x : np.array
        x-axis.
    yaxisList : list
        List of potential y-axis.
    z : np.array
        z-axis.
    ynamelist : list
        Name list of potential y-axis.
    zname : str
        Name of z-axis.
    yunitlist : list
        Unit list of y-axis.
    zunit : str
        Unit of z-axis.

    """
    if not file:
        file = get_hdf5_path()
    with h5py.File(file, 'r') as f:
        # read y axis data
        ynamelist, yaxisList, dimList = _sort_Data_ys(f)
        # read x, z axis data
        x, z, zname = _sort_Traces_xz(f, log_ch_idx, dimList)
        yunitlist = [
            _get_unit(f, yname) if yname else '' for yname in ynamelist
            ]
        zunit = _get_unit(f, zname)
    return x, yaxisList, z, ynamelist, zname, yunitlist, zunit


def get_VNA_Data(file: str = None, bypass: bool = False,
                 bg_row: int = None, collapse_yz: bool = False):
    """
    Get VNA data and slice into a Fortran-style data array.

    Parameters
    ----------
    file : str, optional
        Path string of the hdf5 file. The default is None.
    bypass : bool, optional
        Set True to load the data from hdf5 without unfolding operation. The
        default is False.
    bg_row : int, optional
        Background row index for VNA data format. The default is None.
    collapse_yz : bool, optional
        Set True to set the output is rank-2, otherwise rank-3. The default is
        False.

    Returns
    -------
    x : np.array
        x-axis.
    list or np.array
        list of y-axis or single y-axis.
    np.array
        Unsliced or sliced z-axis.
    xname : str
        x-axis name.
    list or str
        list of y-axis name or single y-axis name.
    zname : str
        z-axis name.

    """
    x, yaxisList, zMesh, ynamelist, zname, yunitlist, _ = open_hdf5(file)
    xname = 'Frequency (Hz)'
    if bypass:
        ynamelist = [
            yname + ' (' + yunit + ')' for yname, yunit in zip(
                ynamelist, yunitlist
                )
            ]
        return x, yaxisList, zMesh, xname, ynamelist, zname
    z, y, yname, yunit = _meshSlice(zMesh, yaxisList, ynamelist, yunitlist)
    yname += (' (' + yunit + ')')
    if bg_row is not None:
        if collapse_yz:
            y, z = y[bg_row], z[:, bg_row]
        else:
            y, z = y[bg_row, np.newaxis], z[:, bg_row, np.newaxis]
    return x, y, z, xname, yname, zname


def get_Digitizer_data(file: str = None, bypass: bool = False):
    """
    Get digitizer data and slice into a Fortran-style data array.

    Parameters
    ----------
    file : str, optional
        Path string of the hdf5 file. The default is None.
    bypass : bool, optional
        Set True to load the data from hdf5 without unfolding operation. The
        default is False.

    Returns
    -------
    x : np.array
        x-axis.
    list or np.array
        list of y-axis or single y-axis.
    np.array
        Unsliced or sliced z-axis.
    xname : str
        x-axis name.
    list or str
        list of y-axis name or single y-axis name.
    zname : str
        z-axis name.

    """
    x, yaxisList, zMesh, ynamelist, zname, yunitlist, zunit = open_hdf5(file)
    xname = 'time (s)'
    zname += (' (' + zunit + ')')
    if bypass:
        ynamelist = [
            yname + ' (' + yunit + ')' for yname, yunit in zip(
                ynamelist, yunitlist
                )
            ]
        return x, yaxisList, zMesh, xname, ynamelist, zname
    z, y, yname, yunit = _meshSlice(zMesh, yaxisList, ynamelist, yunitlist)
    yname += (' (' + yunit + ')')
    return x, y, z, xname, yname, zname


# file management
def copy_hdf5(file: str, prefix: str = '', suffix: str = ''):
    """
    Copy a hdf5 file.

    Parameters
    ----------
    file : str
        File to be copied.
    prefix : str, optional
        Filename prefix. The default is ''.
    suffix : str, optional
        Filename suffix. The default is ''.

    Returns
    -------
    sv_file : str
        Name of the newly created file.

    """
    # copy data/setup to destination
    directory, filename = os.path.split(file)
    filename, extension = os.path.splitext(filename)
    sv_file = os.path.join(directory, prefix + filename + suffix + extension)
    copyfile(file, sv_file)
    return sv_file


def add_to_hdf5(data: np.array, channel: str, file: str,
                unit: str = None, prefix: str = '', suffix: str = ''):
    """
    Add log channel data to the existed hdf5 file.

    Parameters
    ----------
    data : np.array
        Data to be saved.
    channel : str
        Name of the new log channel.
    file : str
        Destination file name.
    unit : str, optional
        Unit of the log channel. The default is None.
    prefix : str, optional
        Prefix for modified log channel name. The default is ''.
    suffix : str, optional
        Suffix for modified log channel name. The default is ''.

    """
    new_ch = prefix + channel + suffix

    with h5py.File(file, 'r+') as f:
        # get reference name
        ref_ch = f['Log list'][0][0]

        # replace Log list
        new_array = np.insert(f['Log list'][:], -1, new_ch)
        del f['Log list']
        f.create_dataset('Log list', data=new_array)

        # Add new Trace properties
        t = f['Traces']
        t.create_dataset(new_ch, data=data)
        t.create_dataset(new_ch + '_N', data=t[ref_ch + '_N'][:])
        t.create_dataset(new_ch + '_t0dt', data=t[ref_ch + '_t0dt'][:])

        # Add new Channels
        ch_duplicate = f['Channels'][_get_unit(f, ref_ch, True)]
        ch_duplicate[0] = new_ch
        if unit is not None:
            ch_duplicate[3] = unit
            ch_duplicate[4] = unit
        new_array = np.insert(f['Channels'][:], -1, ch_duplicate)
        del f['Channels']
        f.create_dataset('Channels', data=new_array)


dtype1stLayer = {
    'Channels': np.dtype(
        [('name', 'O'), ('instrument', 'O'), ('quantity', 'O'),
         ('unitPhys', 'O'), ('unitInstr', 'O'), ('gain', '<f8'),
         ('offset', '<f8'), ('amp', '<f8'), ('highLim', '<f8'),
         ('lowLim', '<f8'), ('outputChannel', 'O'), ('limit_action', 'O'),
         ('limit_run_script', '?'), ('limit_script', 'O'),
         ('use_log_interval', '?'), ('log_interval', '<f8'),
         ('limit_run_always', '?')]
        ),
    'Instrument config': None,
    'Instruments': np.dtype(
        [('hardware', 'O'), ('version', 'O'), ('id', 'O'), ('model', 'O'),
         ('name', 'O'), ('interface', '<i2'), ('address', 'O'),
         ('server', 'O'), ('startup', '<i2'), ('lock', '?'),
         ('show_advanced', '?'), ('Timeout', '<f8'), ('Term. character', 'O'),
         ('Send end on write', '?'), ('Lock VISA resource', '?'),
         ('Suppress end bit termination on read', '?'),
         ('Use VICP protocol', '?'), ('Baud rate', '<f8'),
         ('Data bits', '<f8'), ('Stop bits', '<f8'), ('Parity', 'O'),
         ('GPIB board number', '<f8'), ('Send GPIB go to local at close', '?'),
         ('PXI chassis', '<f8'), ('Run in 32-bit mode', '?')]
        ),
    'Log list': np.dtype([('channel_name', 'O')]),
    'Settings': None,
    'Step config': None,
    'Step list': np.dtype(
        [('channel_name', 'O'), ('step_unit', '<i2'), ('wait_after', '<f8'),
         ('after_last', '<i2'), ('final_value', '<f8'), ('use_relations', '?'),
         ('equation', 'O'), ('show_advanced', '?'), ('sweep_mode', '<i2'),
         ('use_outside_sweep_rate', '?'), ('sweep_rate_outside', '<f8'),
         ('alternate_direction', '?')]
        ),
    'Tags': None,
    'Data': None,
    'Traces': None,
    'Views': None,
    }

dtype2ndLayer = {
    # Costum Instrument config Entries
    # Costum Step config Entries
    'Channel names': np.dtype([('name', 'O'), ('info', 'O')]),
    'Data': np.dtype('<f8'),
    'Time stamp': np.dtype('<f8'),
    # Costum Traces Entries
    'Current view': None,
    }


if __name__ == '__main__':
    # x, y, z, xname, yname, zname = get_Digitizer_data()
    # x, y, z, xname, yname, zname = get_VNA_Data()
    # plot(x, y, z, xname, yname, zname)
    # x, yaxisList, z, _, _, _, _ = open_hdf5()
    pass
