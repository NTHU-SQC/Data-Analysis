# -*- coding: utf-8 -*-
import os
import sys
import h5py
import numpy as np
import pandas as pd
import tkinter
from tkinter import filedialog

try:
    apiFolder = 'Script'
    LabberAPI_Path = os.path.join(os.getcwd(), apiFolder)
    sys.path.append(LabberAPI_Path)
    import Labber
except ModuleNotFoundError:
    print('labber api import error')

def fileStructTraverse(rootDirPath:str):
    """
    Search through all files under the current directory,
    and store the corresponding file name and its path in a dictionary. 

    Parameters
    ----------
    rootDirPath : str
        The absolute path of the current directory.
    Returns
    -------
    fStruct : dict
        A dictionary records a variety of the file name,
        and its corresponding complete path.
        The output dictionary, and its structure just like the below format.
        {'fileName': 'fileStruct'}
        
    """
    fStruct = {}
    for dirName, subdirList, fileList in os.walk(rootDirPath):
        for fname in fileList:
            fStruct[fname] = os.path.join(dirName, fname)
    return fStruct
    
def findKeywordInDB(keyword:str, fileStruct:dict):
    """
    Get the filtered fileStruct(fStruct) with keyword.

    Parameters
    ----------
    keyword : str
        The specified string to filter the fileStruct
    fileStruct : dict
        The input dictionary, and its structure just like the below format.
        {'fileName': 'fileStruct'}
    Returns
    -------
    1. return fStruct
        {'fileNameWithFilter': 'filePathWithFilter'}
    2. return a error message.

    """
    fStruct = {}
    for fname, fpath in fileStruct.items():
        if keyword in fname:
            fStruct[fname] = fpath
        else:
            continue
    if fStruct == {}:
        return f'After this searching, any file name including "{keyword}"'+\
            ' is not found in this database.'
    else:
        return fStruct

def h5DatasetTraverse(filePath:str):
    """
    View the experiment file data structure in *.hdf5 

    Parameters
    ----------
    filePath : str
        The complete path of the file of *.hdf5.

    Returns
    -------
    Data Structure of the specified experimental log file(*.hdf5).

    """
    def _h5_visit_func(name, node) :
        if isinstance(node, h5py.Dataset):
            print(node.name)
    with h5py.File(filePath, 'r') as h5r:
        h5r.visititems(_h5_visit_func)

def getVNAData(filePath:str, bg_row=None):
    """
    Get a variety of measured data from the experimental log file(*.hdf5).

    Parameters
    ----------
    filePath : str
        The complete path of the file of *.hdf5.
    bg_row : TYPE, optional
        Return the first trace as the background signal if bg_row is 0. 
        The default is None.

    Returns
    -------
    S21 : complex vector
        the reflected signal.
    xname : str
        x-axis name.
    xdata : array
        x-axis data.
    yname : str
        y-axis name.
    ydata : array
        y-axis data.
    zname : str
        z-axis name.
    channel_properties : dict
        properties.

    """
    with h5py.File(filePath, 'r') as f:
        # complex array
        S21 = f['Traces/VNA - S21'][:][:, 0, :] +\
            1j * f['Traces/VNA - S21'][:][:, 1, :] 
        # other properties
        pnts = f['Traces/VNA - S21_N'][:][0]
        start = f['Traces/VNA - S21_t0dt'][:][0][0]
        step = f['Traces/VNA - S21_t0dt'][:][0][1]
        xname = 'Frequency'
        xdata = np.arange(start, start+step*pnts, step)
        channel_properties = f['Channels'][:]
        
        try:
            yname = f['Data/Channel names'][:][0][0]
            zname = f['Log list'][:][0][0]
            ydata = f['Data/Data'][:][:, 0, 0]
        except(IndexError):
            yname = ''
            zname = ''
            ydata = np.array([0])
            bg_row = None
            
    if bg_row is None:
        return S21, xname, xdata, yname, ydata, zname, channel_properties
    else:
        return np.reshape(S21[:, bg_row], (len(S21[:, bg_row]), 1)), \
            xname, xdata, yname, ydata[bg_row], zname, channel_properties

    
def getLabberData(filePath: str):
    """
    Get a variety of measured data from the experimental log file(*.hdf5).
    p.s. This function requires to use the Labber API
    Parameters
    ----------
    filePath : str
         The complete path of the file of *.hdf5.

    Returns
    -------
    xdata : TYPE
        x-axis data.
    ydata : TYPE
        y-axis data.
    zdata : TYPE
        z-axis data.

    """
    try:
        f = Labber.LogFile(filePath)
    except FileNotFoundError as err:
        print(f'Error: {err}')
    
    getDataName = f.getLogChannels()[0]['name']
    properties = f.getEntry(-1)
    
    if 'VNA' in getDataName:
        instName = getDataName.split(' - ')[0]
        xdata = np.linspace(properties[f'{instName} - Start frequency'],
                            properties[f'{instName} - Stop frequency'],
                            int(properties[f'{instName} - # of points'])
                            )
        xname = 'Frequency'
        xunit = 'Hz'
    elif 'Alazar' in getDataName:
        start, delta, pts =\
            properties[getDataName]['t0'], \
            properties[getDataName]['dt'], \
            len(properties[getDataName]['y'])
        xdata = np.array([start+idx*delta for idx in range(pts)], dtype=float)
        xname = 'Time'
        xunit = 's'
    
    ydata, yname, yunit =\
            f.getStepChannels()[0]['values'], \
            f.getStepChannels()[0]['name'], \
            f.getStepChannels()[0]['unit']
    zdata = f.getData(getDataName)
    zunit = f.getLogChannels()[0]['unit']
    return xdata, ydata, zdata

def csvExport(exportCSVName:str, properties:list):
    """
    Convert the properties to csv file.
    
    Parameters
    ----------
    exportCSVName : str
        csvName.
    properties : list
        [xdata, ydata, s21].

    Returns
    -------
     *_mag.csv, *_phase.csv, *_parameters.csv
     The above converted files will be stored in the specified directory
     named "MeasureData2CSV".

    """
    csvStorePath = os.path.join(os.getcwd(), 'MeasureData2CSV')
    if not os.path.isdir(csvStorePath):
        os.mkdir(csvStorePath)
    
    # vna data convert
    xdata, ydata, s21 = properties[0], properties[1], properties[2]
    s21_mag, s21_phase = np.abs(s21), np.angle(s21)
    
    # generate csv files
    dfMag, dfPhase = pd.DataFrame(s21_mag), pd.DataFrame(s21_phase)
    if len(xdata) == 1:
        dfParams = pd.DataFrame(
            [
                [xdata[0], ydata[0]],
                [xdata[-1], ydata[-1]],
                [xdata[-1]-xdata[0], ydata[-1]-ydata[0]]
            ]
        )
    else:
        dfParams = pd.DataFrame(
            [
                [xdata[0], ydata[0]],
                [xdata[-1], ydata[-1]],
                [xdata[-1]-xdata[0], ydata[-1]-ydata[0]]
            ]
        )
        
    for dfObj, cfg in zip([dfMag, dfPhase, dfParams],
                             ['mag', 'phase', 'parameters']):
        cfgName = f'{exportCSVName}_{cfg}.csv'
        dfObj.to_csv(os.path.join(csvStorePath, cfgName),
                     index=False, header=False)
        
def csvExport2Folder(exportCSVName:str, properties:list, exportPath:str):
    """
    Convert the properties to csv file.
    
    Parameters
    ----------
    exportCSVName : str
        csvName.
    properties : list
        [xdata, ydata, s21].

    Returns
    -------
     *_mag.csv, *_phase.csv, *_parameters.csv
     The above converted files will be stored in the specified directory
     named "MeasureData2CSV".

    """
    # csvStorePath = os.path.join(os.getcwd(), 'MeasureData2CSV')
    # if not os.path.isdir(csvStorePath):
    #     os.mkdir(csvStorePath)
    csvStorePath = exportPath
    
    # vna data convert
    xdata, ydata, s21 = properties[0], properties[1], properties[2]
    s21_mag, s21_phase = np.abs(s21), np.angle(s21)
    
    # generate csv files
    dfMag, dfPhase = pd.DataFrame(s21_mag), pd.DataFrame(s21_phase)
    if len(xdata) == 1:
        dfParams = pd.DataFrame(
            [
                [xdata[0], ydata[0]],
                [xdata[-1], ydata[-1]],
                [xdata[-1]-xdata[0], ydata[-1]-ydata[0]]
            ]
        )
    else:
        dfParams = pd.DataFrame(
            [
                [xdata[0], ydata[0]],
                [xdata[-1], ydata[-1]],
                [xdata[1]-xdata[0], ydata[1]-ydata[0]]
            ]
        )
        
    for dfObj, cfg in zip([dfMag, dfPhase, dfParams],
                             ['mag', 'phase', 'parameters']):
        cfgName = f'{exportCSVName}_{cfg}.csv'
        dfObj.to_csv(os.path.join(csvStorePath, cfgName),
                     index=False, header=False)
        
def addColRowName2CSV(csvStorePath:str,
                      clist:list,
                      rlist:list,
                      unitlist:list):
    
    df = pd.read_csv(csvStorePath, names=clist)
    df.insert(0, "Item", rlist, True)
    
    addrow = {}
    for key, item in zip(df.columns, ['unit'] + unitlist):
        addrow[key] = item
    
    df = df.append(addrow, ignore_index=True)
    print(df)
    
def csvImport(filePath:str, transpose:bool = False):
    """
    Import the CSV experiment file, and return its corresponding array.

    Parameters
    ----------
    filePath : str
        The complete path of the CSV file.

    Returns
    -------
    Array
        Data Stored in array.

    """
    try:
        df = pd.read_csv(filePath, sep=',', header=None)
        if transpose == False:
            return df.values
        else:
            return df.values.transpose()
    except FileNotFoundError as err:
        print(f'Error: {err}')

def get_hdf5_path(title='Select item'):
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return filedialog.askopenfilename(
        filetypes=[('.HDF Files', '.hdf5')],
        title=title)

if __name__ == '__main__':
    from tqdm import tqdm
    
    ## automatic hdf5 to csv convert
    # Get the complete path of the specified folder called "MeasureData"
    # rootDir = os.path.join(os.getcwd(), 'MeasureData')
    
    # Traverse all files under the current directory,
    #　and store the corresponding file name and its path in a dictionary. 
    # database = fileStructTraverse(rootDir)
    
    # Get the filtered database with the filterdWord as the key in dictionary.
    # filtedWord = ''
    # filteredDB = findKeywordInDB(filtedWord, database)
    
    # Batch data conversion to CSV files
    # for fname, fpath in tqdm(filteredDB.items()):
    #     # s21, _, xdata, _, ydata, _, _ = getVNAData(fpath)
    #     # csvExport(fname.replace('.hdf5', ''), [xdata, ydata, s21])
    #     xdata, ydata, zdata = getLabberData(fpath)
    #     csvExport(fname.replace('.hdf5', ''), [xdata, ydata, zdata])
    
    ## manually convert hdf5 to csv files
    fpath = get_hdf5_path()
    xdata, ydata, zdata = getLabberData(fpath)
    fileName, filePath = os.path.split(fpath)[1], os.path.split(fpath)[0]
    csvExport2Folder(fileName.replace('.hdf5', ''),
                      [xdata, ydata, zdata],
                      filePath)
    
    # debug
    # csvPath = r"H:\210723_S1\TD\Extracted\4.3GHz\Normalized_sub_S1_Rabi_dark_bright_state_4.31GHz_1_parameters.csv"
    # col = ['xdata', 'ydata']
    # row = ['start', 'stop', 'step']
    # unit = ['s', 'dB']
    # addColRowName2CSV(csvPath, col, row, unit)