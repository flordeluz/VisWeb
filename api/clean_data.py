import matplotlib.pyplot as plt
import pandas as pd

import numpy as np
from sklearn.base import _pprint
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, SimpleImputer, IterativeImputer

knn_imputer = KNNImputer(missing_values=-1, n_neighbors=10, weights="distance")
simple_imp = SimpleImputer(missing_values=-1, strategy='mean')
iter_imp = IterativeImputer(
    missing_values=-1, max_iter=20)

# imputer.fit_transform(X)
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


def modify_external_array(x):
    global datasets
    dx = datasets[:]
    dx.append(x)
    datasets = dx


def see_global_data():
    print(datasets)


dates, data = read_dataset('majes')

print(dates[9932], dates[10986])

# dates, data = read_dataset('joya')

# range_data = range(len(data))

# data = np.array(data)

# print(data.shape)

# data[data < 0] = -1
# back_data = data[:]

# # data = simple_imp.fit_transform(data)
# # data = iter_imp.fit_transform(data)
# data = knn_imputer.fit_transform(data)


# print(data.shape)


# fig, axs = plt.subplots(2, sharex=True, sharey=True)
# axs[0].plot(back_data)
# axs[0].legend(['prec', 'temp Max', 'tempMin'])
# axs[1].plot(data)
# plt.show()
