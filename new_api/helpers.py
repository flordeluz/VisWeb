
import numpy as np
import pandas as pd
from scipy import fft
from scipy import signal as sig


def get_period_days(dataframe, resample="W", feature=1):
    res_dataframe = dataframe.resample(resample).mean()

    y = res_dataframe.values[:,2]
    fourier_output = np.abs(fft.fft(y))
    frecuencies = fft.fftfreq(len(y))
    peaks = sig.find_peaks(fourier_output, prominence=10**2)[0]

    print(peaks)
    peak_freq = frecuencies[peaks]
    peak_power = fourier_output[peaks]

    output = pd.DataFrame()

    output['index'] = peaks
    output['freq (1/hour)'] = peak_freq
    output['amplitude'] = peak_power
    output['period (days)'] = 1/peak_freq
    output['fft'] = fourier_output[peaks]
    output = output.sort_values('amplitude', ascending=False)
    max_amp_period = output['period (days)'].iloc[0:5:2]
    if len(max_amp_period) == 0:
        return 0
    print(output,max_amp_period[0])
    return max_amp_period[0]

    
