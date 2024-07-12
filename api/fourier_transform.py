import numpy as np
from scipy import fftpack
import matplotlib.pyplot as plt
import pandas as pd
from scipy import fft
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.impute import SimpleImputer
from scipy import signal as sig


datasets = ['chiguata', 'joya', 'majes', 'pampilla']


def read_dataset(dataset):
    if dataset not in datasets:
        return 'Dataset not found'
    file_lines = open(f'Datos/{dataset}.txt', 'r').readlines()
    data = []
    dates = []
    for line in file_lines:
        year, month, day, precipitation, tempMax, tempMin = line.split(' ')

        data.append([
            float(precipitation),
            float(tempMax),
            float(tempMin)
        ])
        dates.append(f'{year}-{month}-{day}')
    return dates, data


def annot_max(x, y, ax=None):
    xmax = x[np.argmax(y)]
    ymax = y.max()
    text = "x={:.3f}, y={:.3f}".format(xmax, ymax)
    if not ax:
        ax = plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops = dict(
        arrowstyle="->", connectionstyle="angle,angleA=0,angleB=60")
    kw = dict(xycoords='data', textcoords="data",
              arrowprops=arrowprops, bbox=bbox_props, ha="left", va="top")
    ax.annotate(text, xy=(xmax, ymax), xytext=(xmax+.5, ymax+5), **kw)


dates, data = read_dataset('joya')
data = np.array(data)
data[data < 0] = -1
prec, tmax, tmin = data[:, 0], data[:, 1], data[:, 2]


simple_imp = SimpleImputer(missing_values=-1, strategy='mean')
data = simple_imp.fit_transform(data)

dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(dates))

resample = 'W'

prec_dataframe = dataframe.resample(resample).max()[0]
tmax_dataframe = dataframe.resample(resample).mean()[1]
tmin_dataframe = dataframe.resample(resample).mean()[2]

choosed_dataframe = tmin_dataframe

series_mean = choosed_dataframe[0].mean()
choosed_dataframe = choosed_dataframe - choosed_dataframe.mean()

y = choosed_dataframe.values
time = choosed_dataframe.index.values


print("Len dataset", len(y))

fourier_output = np.abs(fft.fft(y))
frecuencies = fft.fftfreq(len(y))


# mask = frecuencies >= 0
# frecuencies = frecuencies[mask]
# fourier_output = fourier_output[mask]
print('Fourier output shape', fourier_output.shape)

fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(15, 5))
ax[0].plot(frecuencies, fourier_output)    # plot fourier result
annot_max(frecuencies, fourier_output, ax[0])


peaks = sig.find_peaks(fourier_output, prominence=10**2)[0]
print(peaks)
peak_freq = frecuencies[peaks]
peak_power = fourier_output[peaks]
ax[0].plot(peak_freq, peak_power, 'ro')


output = pd.DataFrame()
output['index'] = peaks
output['freq (1/hour)'] = peak_freq
output['amplitude'] = peak_power
output['period (days)'] = 1/peak_freq * 30
output['fft'] = fourier_output[peaks]
output = output.sort_values('amplitude', ascending=False)

print(output)

max_amp_index = output['index'].iloc[0:5:2]

print("Maximum amplitude", max_amp_index.values)

filtered_fft_output = np.array(
    [f if i in max_amp_index.values else 0 for i, f in enumerate(fourier_output)])
filtered_sig = fft.ifft(filtered_fft_output)

print("output shape:", filtered_fft_output.shape, fourier_output.shape, y.shape)

print("type", type(filtered_sig.astype('float')[0]))

N = -1

ax[1].plot(time[:N], y[:N],
           linewidth=1, label='Original serie')
ax[1].plot(time[:N], filtered_sig[:N].real,
           linewidth=1, label='Filtered serie')

ax[0].set_title('Frecuency domain')
ax[1].set_title('Fourier inverted')

# ax[1].plot()  #
plt.show()
