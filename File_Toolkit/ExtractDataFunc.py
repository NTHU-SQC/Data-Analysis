import numpy as np
import h5py
import Labber


def readFSweepDat(file):
    Background = np.loadtxt(file, skiprows=1)
    BackFreq = Background[:, 0]
    BackPhase = np.unwrap(Background[:, 1])
    BackAmp = Background[:, 2]
    BackComplex = BackAmp * np.exp(1j * BackPhase)
    return [BackFreq, BackComplex]


def readFSweepLabber(file):
    ATS_var = 'Alazar - Channel A - Average demodulated value'
    BackFreq_var = 'Qubit - Frequency'
    LogData = Labber.LogFile(file)
    BackComplex = np.conj(LogData.getData(ATS_var)[0])
    BackFreq = LogData.getData(BackFreq_var)[0] * 1e-9
    return [BackFreq, BackComplex]


def readFISweepDat(file):
    # for HQC data
    OneTone = np.loadtxt(file, skiprows=1)
    OneCurrent = OneTone[:, 0]
    OneCurrentUniq = np.unique(OneCurrent)
    NumCurrent = np.size(OneCurrentUniq)
    OneFreq = OneTone[:, 1]
    OneFreqUniq = np.unique(OneFreq)
    NumFreq = np.size(OneFreqUniq)
    if NumCurrent * NumFreq > np.size(OneCurrent):
        NumCurrent = NumCurrent - 1
        OneCurrent = OneCurrent[0:NumCurrent * NumFreq]
        OneFreq = OneFreq[0:NumCurrent * NumFreq]
        OneTone = OneTone[0:NumCurrent * NumFreq, :]

    OneCurrent = np.transpose(np.reshape(OneCurrent, (NumCurrent, NumFreq)))
    OneFreq = np.transpose(np.reshape(OneFreq, (NumCurrent, NumFreq)))
    OnePhase = np.unwrap(np.transpose(np.reshape(OneTone[:, 2], (NumCurrent, NumFreq))), axis=0)
    OneAmp = np.transpose(np.reshape(OneTone[:, 3], (NumCurrent, NumFreq)))
    OneComplex = OneAmp * np.exp(1j * OnePhase)
    return [OneFreq, OneCurrent, OneComplex]


def readFISweepLabber(file):
    ATS_var = 'Alazar - Channel A - Average demodulated value'
    OneFreq_var = 'Qubit - Frequency'
    Current_var = 'Yoko - Current'
    LogData = Labber.LogFile(file)
    OneComplex = np.conj(np.transpose(LogData.getData(ATS_var)))
    OneFreq = np.transpose(LogData.getData(OneFreq_var)) * 1e-9
    OneCurrent = np.transpose(LogData.getData(Current_var)) * 1000
    return [OneFreq, OneCurrent, OneComplex]


def readFISweepTwoToneLabber(file):
    ATS_var = 'Alazar - Channel A - Average demodulated value'
    OneFreq_var = 'Pump - Frequency'
    Current_var = 'Yoko - Current'
    LogData = Labber.LogFile(file)
    OneComplex = np.conj(np.transpose(LogData.getData(ATS_var)))
    OneFreq = np.transpose(LogData.getData(OneFreq_var)) * 1e-9
    OneCurrent = np.transpose(LogData.getData(Current_var)) * 1000
    return [OneFreq, OneCurrent, OneComplex]


def readFSweepTwoToneLabber(file):
    ATS_var = 'Alazar - Channel A - Average demodulated value'
    OneFreq_var = 'Pump - Frequency'
    LogData = Labber.LogFile(file)
    OneComplex = np.conj((LogData.getData(ATS_var)))[0]
    OneFreq = (LogData.getData(OneFreq_var))[0] * 1e-9
    return [OneFreq, OneComplex]


def readFPSweepDat(file):
    # for HQC data
    OneTone = np.loadtxt(file, skiprows=1)
    OnePower = OneTone[:, 0]
    OnePowerUniq = np.unique(OnePower)
    NumPower = np.size(OnePowerUniq)
    OneFreq = OneTone[:, 1]
    OneFreqUniq = np.unique(OneFreq)
    NumFreq = np.size(OneFreqUniq)
    if NumPower * NumFreq > np.size(OnePower):
        NumPower = NumPower - 1
        OneTone = OneTone[0:NumPower * NumFreq, :]
        OnePower = OneTone[:, 0]
        OneFreq = OneTone[:, 1]
    OnePower = np.transpose(np.reshape(OnePower, (NumPower, NumFreq)))
    OneFreq = np.transpose(np.reshape(OneFreq, (NumPower, NumFreq)))
    OnePhase = np.unwrap(np.transpose(np.reshape(OneTone[:, 2], (NumPower, NumFreq))), axis=0)
    OneAmp = np.transpose(np.reshape(OneTone[:, 3], (NumPower, NumFreq)))
    OneComplex = OneAmp * np.exp(1j * OnePhase)
    return [OneFreq, OnePower, OneComplex]


def readFPSweepLabber(file):
    ATS_var = 'Alazar - Channel A - Average demodulated value'
    OneFreq_var = 'Qubit - Frequency'
    Power_var = 'Qubit - Power'
    LogData = Labber.LogFile(file)
    OneComplex = np.conj(np.transpose(LogData.getData(ATS_var)))
    OneFreq = np.transpose(LogData.getData(OneFreq_var)) * 1e-9
    OnePower = np.transpose(LogData.getData(Power_var))
    return [OneFreq, OnePower, OneComplex]


def readQubitPowerLabber(file):
    Power_var = 'Qubit - Power'
    LogData = Labber.LogFile(file)
    Power = np.unique(np.transpose(LogData.getData(Power_var)))
    if len(Power) == 1:
        Power = Power[0]
    return Power


def readQubitFreqLabber(file):
    Freq_var = 'Qubit - Frequency'
    LogData = Labber.LogFile(file)
    Freq = np.unique(np.transpose(LogData.getData(Freq_var))) * 1e-9
    if len(Freq) == 1:
        Freq = Freq[0]
    return Freq


def readPumpPowerLabber(file):
    Power_var = 'Pump - Power'
    LogData = Labber.LogFile(file)
    Power = np.unique(np.transpose(LogData.getData(Power_var)))
    if len(Power) == 1:
        Power = Power[0]
    return Power


def readPumpFreqLabber(file):
    Freq_var = 'Pump - Frequency'
    LogData = Labber.LogFile(file)
    Freq = np.unique(np.transpose(LogData.getData(Freq_var))) * 1e-9
    if len(Freq) == 1:
        Freq = Freq[0]
    return Freq


def readCurrentLabber(file):
    Cur_var = 'Yoko - Current'
    LogData = Labber.LogFile(file)
    Cur = np.unique(np.transpose(LogData.getData(Cur_var))) * 1e3
    if len(Cur) == 1:
        Cur = Cur[0]
    return Cur

def getFolder(file, LabberFolder='C:\\Users/admin\Labber\Data/'):
    name_str_list = file.split('_')
    type_str = name_str_list[0]
    date_str_lsit = name_str_list[-1].split('-')
    year = date_str_lsit[0]
    month = date_str_lsit[1]
    day = date_str_lsit[2]
    file_folder = LabberFolder + year + '\\' + month + '\\' + 'Data_' + month + day + '\\'
    return file_folder

def readDrivingPulseLenLabber(file):
    PulseLen_var = 'Pulse Generator - Width #1'
    LogData = Labber.LogFile(file)
    PulseLen = np.unique(np.transpose(LogData.getData(PulseLen_var)))
    if len(PulseLen) == 1:
        PulseLen = PulseLen[0]
    return PulseLen


def readRabiH5(file):
    # for HQC data
    f = h5py.File(file, 'r')
    key_list = list(f.keys())

    # Get the data
    rabi_time = list(f[key_list[2]])[0]
    rabi_amp = list(f[key_list[0]])[0][0]
    rabi_phase = list(f[key_list[1]])[0][0]
    rabi_complex = rabi_amp * np.exp(1j * rabi_phase)
    rabi_complex1 = rabi_complex[0::2]
    rabi_complex2 = rabi_complex[1::2]
    return [rabi_time, rabi_complex1, rabi_complex2]


def readRabiLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Width #1'
    LogData = Labber.LogFile(file)
    rabi_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, 0]
    rabi_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9

    return [rabi_time, rabi_complex]


def readRabiPowerSweepLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Width #1'
    Power_var = 'Pump - Power'
    LogData = Labber.LogFile(file)
    rabi_power = np.unique(np.transpose(LogData.getData(Power_var)))
    rabi_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9
    rabi_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, ::len(rabi_time)]

    return [rabi_time, rabi_power, rabi_complex]


def readRabiFreqSweepLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Width #1'
    Freq_var = 'Qubit - Frequency'
    LogData = Labber.LogFile(file)
    rabi_freq = np.unique(np.transpose(LogData.getData(Freq_var))) * 1e-9
    rabi_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9
    rabi_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, ::len(rabi_time)]

    return [rabi_time, rabi_freq, rabi_complex]


def readT1H5(file):
    # for HQC data
    f = h5py.File(file, 'r')
    key_list = list(f.keys())

    # Get the data
    t1_time = list(f[key_list[0]])[0]
    t1_amp = list(f[key_list[1]])[0][0]
    t1_phase = list(f[key_list[2]])[0][0]
    t1_complex = t1_amp * np.exp(1j * t1_phase)
    t1_complex1 = t1_complex[0::2]
    t1_complex2 = t1_complex[1::2]
    return [t1_time, t1_complex1, t1_complex2]


def readT1Labber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Readout delay'
    LogData = Labber.LogFile(file)
    t1_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, 0]
    t1_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9

    return [t1_time, t1_complex]


def readT1PowerSweepLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Readout delay'
    Power_var = 'Pump - Power'
    LogData = Labber.LogFile(file)
    t1_power = np.unique(np.transpose(LogData.getData(Power_var)))
    t1_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9
    t1_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, ::len(t1_time)]

    return [t1_time, t1_power, t1_complex]


def readRepeatedT1SweepLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Readout delay'
    Counter_var = 'Counter - Number of points'
    LogData = Labber.LogFile(file)
    t1_counter = np.unique(np.transpose(LogData.getData(Counter_var)))
    t1_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9
    t1_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, ::len(t1_time)]

    return [t1_time, t1_counter, t1_complex]


def readRepeatedFSweepTwoToneLabber(file, ATS_var='Alazar - Channel A - Average demodulated value',
                                    Freq_var='Pump - Frequency', Counter_var='Counter - Number of points'):
    # for Labber data
    LogData = Labber.LogFile(file)
    complex = np.conj(np.transpose(LogData.getData(ATS_var)))
    freq = np.transpose(LogData.getData(Freq_var)) * 1e-9
    counter = np.transpose(LogData.getData(Counter_var))

    return [freq, counter, complex]


def readT2H5(file):
    # for HQC data
    f = h5py.File(file, 'r')
    key_list = list(f.keys())

    # Get the data
    t1_time = list(f[key_list[2]])[0]
    t1_amp = list(f[key_list[0]])[0][0]
    t1_phase = list(f[key_list[1]])[0][0]
    t1_complex = t1_amp * np.exp(1j * t1_phase)
    return [t1_time, t1_complex]


def readT2Labber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Sequence duration'
    LogData = Labber.LogFile(file)
    t2_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, 0]
    t2_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9

    return [t2_time, t2_complex]


def readRepeatedT2SweepLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Sequence duration'
    Counter_var = 'Counter - Number of points'
    LogData = Labber.LogFile(file)
    t2_counter = np.unique(np.transpose(LogData.getData(Counter_var)))
    t2_time = np.transpose(LogData.getData(Time_var))[:, 0] * 1e9
    t2_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, ::len(t2_time)]
    return [t2_time, t2_counter, t2_complex]


def readRepeatedT1T2InterleavedSweepLabber(file):
    # for Labber data
    ATS_var = 'Alazar - Channel A - Average buffer demodulated values'
    Time_var = 'Pulse Generator - Sequence duration'
    Counter_var = 'Counter - Number of points'
    LogData = Labber.LogFile(file)
    counter = np.unique(np.transpose(LogData.getData(Counter_var)))
    num_time = int(len(np.transpose(LogData.getData(Time_var))[0, :]) / len(counter))
    time = np.transpose(LogData.getData(Time_var))[0, :num_time] * 1e9
    t1_t2_complex = np.conj(np.transpose(LogData.getData(ATS_var)))[:, ::len(time) * 2]
    t1_complex = t1_t2_complex[0::2]
    t2_complex = t1_t2_complex[1::2]
    return [time, counter, t1_complex, t2_complex]


def readVNAS11(file):
    # for Labber data
    S11_var = 'VNA - S11'
    start_freq_var = 'VNA - Start frequency'
    stop_freq_var = 'VNA - Stop frequency'
    num_of_points_var = 'VNA - # of points'
    LogData = Labber.LogFile(file)
    S11_complex = (np.transpose(LogData.getData(S11_var)))[:, 0]
    Start_freq = np.transpose(LogData.getData(start_freq_var))[:, 0] * 1e-9
    Stop_freq = np.transpose(LogData.getData(stop_freq_var))[:, 0] * 1e-9
    Num_of_points = len(S11_complex)
    freq = np.linspace(Start_freq, Stop_freq, Num_of_points)

    return [freq, S11_complex]


def readVNAS21(file):
    # for Labber data
    S11_var = 'VNA - S21'
    start_freq_var = 'VNA - Start frequency'
    stop_freq_var = 'VNA - Stop frequency'
    num_of_points_var = 'VNA - # of points'
    LogData = Labber.LogFile(file)
    S11_complex = (np.transpose(LogData.getData(S11_var)))[:, 0]
    Start_freq = np.transpose(LogData.getData(start_freq_var))[:, 0] * 1e-9
    Stop_freq = np.transpose(LogData.getData(stop_freq_var))[:, 0] * 1e-9
    Num_of_points = len(S11_complex)
    freq = np.linspace(Start_freq, Stop_freq, Num_of_points)

    return [freq, S11_complex]
