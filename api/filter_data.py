import matplotlib
import statsmodels.api as sm
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from pandas.core.groupby.generic import DataFrameGroupBy
from sklearn.impute import SimpleImputer

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


dates, data = read_dataset('joya')

data = np.array(data)
data[data < 0] = -1

simple_imp = SimpleImputer(missing_values=-1, strategy='mean')
data = simple_imp.fit_transform(data)

dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(dates))
# dataframe.index = pd.to_datetime(dataframe.index)

resample = 'W'

res_dataframe = dataframe.resample(resample).mean()
prec_dataframe = dataframe.resample(resample).max()[0]
tmax_dataframe = dataframe.resample(resample).mean()[1]
tmin_dataframe = dataframe.resample(resample).mean()[2]

print(dataframe)

print(res_dataframe)

# fig, axs = plt.subplots(2, sharex=True, sharey=True)
# axs[0].plot(dataframe.index.values, dataframe[0], '.-', )
# axs[0].plot(dataframe.index.values, dataframe[1], '.-', )
# axs[0].plot(dataframe.index.values, dataframe[2], '.-', )
# # axs[1].plot(res_dataframe.index.values, res_dataframe, '.-')
# axs[1].plot(preq_dataframe.index.values, preq_dataframe, '.-')
# axs[1].plot(tmax_dataframe.index.values, tmax_dataframe, '.-')
# axs[1].plot(tmin_dataframe.index.values, tmin_dataframe, '.-')
# # plt.setp(axs[0], xticks=axs[0].get_xticklabels(), visible=True)
# axs[0].tick_params(axis='both', which='both', labelbottom=True)
# plt.show()

res_dataframes = {'Precipitation': prec_dataframe,
                  'Temp. max': tmax_dataframe,
                  'Temp. min': tmin_dataframe
                }

matplotlib.rcParams['figure.figsize'] = [18.0, 8.0]
for name, cur_dataframe in res_dataframes.items():
    fig, axes = plt.subplots(4, 1, sharex=True)
    fig.suptitle(name + ' Feature', fontsize=16)
    decomposition = sm.tsa.seasonal_decompose(cur_dataframe, model="aditive")

    print("Kheee", decomposition.trend.values)

    decomposition.observed.plot(ax=axes[0], legend=False)
    axes[0].set_ylabel('Observed')
    decomposition.trend.plot(ax=axes[1], legend=False, color='g')
    axes[1].set_ylabel('Trend')
    decomposition.seasonal.plot(ax=axes[2], legend=False, color="tab:orange")
    axes[2].set_ylabel('Seasonal')
    decomposition.resid.plot(ax=axes[3], legend=False, color='k')
    axes[3].set_ylabel('Residual')

    axes[0].tick_params(axis='both', which='both', labelbottom=True)
    axes[1].tick_params(axis='both', which='both', labelbottom=True)
    axes[2].tick_params(axis='both', which='both', labelbottom=True)
    axes[3].tick_params(axis='both', which='both', labelbottom=True)

    # figure = decomposition.plot()
    plt.show()
