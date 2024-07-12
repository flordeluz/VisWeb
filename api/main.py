import json

import bottle
import numpy as np
import pandas as pd
import simplejson
import statsmodels.api as sm
from bottle import request, response, route, static_file, view
from matplotlib.pyplot import table
from scipy import fft
from scipy import signal as sig
from sklearn.decomposition import PCA
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler

minmax_scaler = MinMaxScaler()
sc_scaler = StandardScaler()

knn_imputer = KNNImputer(missing_values=-1, n_neighbors=10, weights="uniform")
simple_imp = SimpleImputer(missing_values=-1, strategy='mean')
iter_imp = IterativeImputer(
    missing_values=-1, max_iter=20)


datasets = ['chiguata', 'joya', 'majes', 'pampilla']
data_headers = ['precipitation', 'tempMax', 'tempMin']

bottle.TEMPLATE_PATH.append('./dist/')


general_data = []
general_dates = []


def read_dataset(dataset):
    print("Len general data:", len(general_data), len(general_dates))
    if dataset not in datasets:
        return 'Dataset not found'
    if len(general_data) != 0 and len(general_dates) != 0:
        return -1
    file_lines = open(f'Datos/{dataset}.txt', 'r').readlines()
    data = []
    dates = []
    for line in file_lines:
        year, month, day, precipitation, tempMax, tempMin = line.strip().split(' ')

        data.append([
            float(precipitation),
            float(tempMax),
            float(tempMin)
        ])
        dates.append(f'{year}-{month}-{day}')
    return dates, data


def build_full_data(dates, data, extra_headers=['precipitation', 'tempMax', 'tempMin'], save_data=True):
    full_data = []
    for i, single_data in enumerate(data):
        data_object = {
            'date': dates[i]
        }

        data_object.update(dict(zip(extra_headers, single_data)))

        full_data.append(data_object)

    if save_data:
        global general_dates, general_data
        general_dates = dates
        general_data = data
    return full_data


def clean_data(data_object):
    for key, value in data_object.items():
        if float(value) < 0:
            value = -1


def enable_cors(fn):
    def wrapper(*args, **kwargs):
        bottle.response.set_header("Access-Control-Allow-Origin", "*")
        bottle.response.set_header(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        bottle.response.set_header(
            "Access-Control-Allow-Headers", "Origin, Content-Type")

        # skip the function if it is not needed
        if bottle.request.method == 'OPTIONS':
            return

        return fn(*args, **kwargs)
    return wrapper


@route('/')
def index():
    return ''


@route('/data/<dataset>')
@enable_cors
def data(dataset):
    if dataset not in datasets:
        return 'Dataset not found'
    file_lines = open(f'Datos/{dataset}.txt', 'r').readlines()
    data = []
    dates = []
    for line in file_lines:
        # print(line.split(' '))
        year, month, day, precipitation, tempMax, tempMin = line.strip().split(' ')

        if float(precipitation) < 0:
            precipitation = -1
        if float(tempMin) < 0:
            tempMin = -1
        if float(tempMax) < 0:
            tempMax = -1

        data_object = {
            'date': f'{year}-{month}-{day}',
            'precipitation': float(precipitation),
            'tempMax': float(tempMax),
            'tempMin': float(tempMin)
        }
        dates.append(f'{year}-{month}-{day}')
        data.append(data_object)

    response.headers['Content-Type'] = 'application/json'

    global general_data, general_dates
    general_dates, general_data = [], []

    return json.dumps(data)


@route('/data/<dataset>/normalize')
@enable_cors
def scale_dataset(dataset):

    response.headers['Content-Type'] = 'application/json'

    read_response = read_dataset(dataset)
    if read_response == -1:
        print('Using general data')
        global general_data, general_dates
        dates = general_dates
        data = general_data
    else:
        dates, data = read_response

    # dates, data = read_dataset(dataset)

    data = np.array(data)

    data[data < 0] = -1
    data = minmax_scaler.fit_transform(data)

    full_data = build_full_data(dates, data)
    return json.dumps(full_data)


@route('/data/<dataset>/reduce/<n_comp>')
@enable_cors
def reduce_dataset(dataset, n_comp):
    response.headers['Content-Type'] = 'application/json'

    read_response = read_dataset(dataset)
    if read_response == -1:
        global general_data, general_dates
        dates = general_dates
        data = general_data
    else:
        dates, data = read_response

    n_comp = int(n_comp)
    pca = PCA(n_comp)
    # dates, data = read_dataset(dataset)
    data = np.array(data)
    data[data < 0] = -1
    data = sc_scaler.fit_transform(data)
    data = pca.fit_transform(data)

    full_data = build_full_data(
        dates, data, extra_headers=range(1, n_comp + 1))
    return json.dumps(full_data)


@route('/data/<dataset>/transform/<factor>')
@enable_cors
def transform_dataset(dataset, factor):
    response.headers['Content-Type'] = 'application/json'

    read_response = read_dataset(dataset)
    if read_response == -1:
        global general_data, general_dates
        dates = general_dates
        data = general_data
    else:
        dates, data = read_response

    # dates, data = read_dataset(dataset)

    data = np.array(data)

    data[data < 0] = -1

    data = float(factor) * data

    full_data = build_full_data(dates, data)

    return json.dumps(full_data)


@route('/data/<dataset>/clean/<method>')
@enable_cors
def clean_dataset(dataset, method):
    response.headers['Content-Type'] = 'application/json'

    read_response = read_dataset(dataset)
    if read_response == -1:
        global general_data, general_dates
        dates = general_dates
        data = general_data
    else:
        print(read_response)
        dates, data = read_response

    data = np.array(data)
    dates = np.array(dates)

    # print(data)
    # print(dates)
    data[data < 0] = -1

    if method == 'clean-knn':
        data = knn_imputer.fit_transform(data)
    elif method == 'clean-mean':
        data = simple_imp.fit_transform(data)

    full_data = build_full_data(dates, data)

    return json.dumps(full_data)


@route('/data/<dataset>/scale')
@enable_cors
def data_scale(dataset):
    response.headers['Content-Type'] = 'application/json'
    read_response = read_dataset(dataset)
    dates, data = read_response

    data = np.array(data)
    dates = np.array(dates)
    data[data < 0] = -1
    data = simple_imp.fit_transform(data)

    dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(dates))
    resample = 'ME'

    # If it's not precipitation then use the mean to resample
    res_dataframe = dataframe.resample(resample).agg({0: np.max, 1: np.max, 2: np.min})

    # print(res_dataframe)

    feature_data = np.array(res_dataframe)
    # print(feature_data)
    # feature_data = np.append(feature_data, np.array(
    #     [res_dataframe.values]).T, axis=1)
    full_data = build_full_data(
        res_dataframe.index.strftime('%Y-%m-%d'), feature_data, extra_headers=['precipitation', 'tempMax', 'tempMin'], save_data=False)
    # return str(full_data)

    response.add_header(
        'Max-Values', f'{np.ceil(res_dataframe[0].max())},{np.ceil(res_dataframe[1].max())},{np.ceil(res_dataframe[2].max())}')

    response.add_header('Access-Control-Expose-Headers', 'Max-Values')
    print(simplejson.dumps(full_data))
    return simplejson.dumps(full_data)
    # return simplejson.dumps(full_data, ignore_nan=True)
    # return res_dataframe


@route('/data/<dataset>/vbehavior/<operator>')
@enable_cors
def vbehavior_analyse(dataset, operator):
    response.headers['Content-Type'] = 'application/json'

    read_response = read_dataset(dataset)
    if read_response == -1:
        global general_data, general_dates
        dates = general_dates
        data = general_data
    else:
        # print(read_response)
        dates, data = read_response

    data = np.array(data)
    dates = np.array(dates)
    data[data < 0] = -1

    if request.query:
        feature = int(request.query.feature)

    dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(dates))
    resample = 'W'

    # If it's not precipitation then use the mean to resample
    if feature > 0:
        res_dataframe = dataframe.resample(resample).mean()[feature]
    # Else use the maxiimum value to resample
    else:
        res_dataframe = dataframe.resample(resample).max()[feature]

    # operator seasonal_decompose
    if operator in ['trend', 'seasonality']:
        decomposition = sm.tsa.seasonal_decompose(
            res_dataframe, model="aditive")
        if operator == 'trend':
            feature_data = decomposition.trend.values
        elif operator == 'seasonality':
            feature_data = decomposition.seasonal.values
        else:
            feature_data = []

    # Fourier
    elif operator == 'cyclicity':
        y = res_dataframe.values
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

        print(output)

        max_amp_index = output['index'].iloc[0:5:2]

        filtered_fft_output = np.array(
            [f if i in max_amp_index.values else 0 for i, f in enumerate(fourier_output)])
        print("Choosed: ", max_amp_index)

        filtered_sig = fft.ifft(filtered_fft_output)
        print("output shape:", filtered_fft_output.shape,
              fourier_output.shape, y.shape)
        feature_data = np.array(filtered_sig.astype('float'))

    feature_data = np.array([feature_data]).T
    feature_data = np.append(feature_data, np.array(
        [res_dataframe.values]).T, axis=1)
    print(feature_data.shape, res_dataframe.values.shape, feature_data)

    full_data = build_full_data(
        res_dataframe.index.strftime('%Y-%m-%d'), feature_data, extra_headers=['result', 'orig'], save_data=False)
    return simplejson.dumps(full_data, ignore_nan=True)


@route('/data/<dataset>/period')
@enable_cors
def get_period(dataset):
    response.headers['Content-Type'] = 'application/json'

    read_response = read_dataset(dataset)
    if read_response == -1:
        global general_data, general_dates
        dates = general_dates
        data = general_data
    else:
        # print(read_response)
        dates, data = read_response

    data = np.array(data)
    dates = np.array(dates)
    data[data < 0] = -1
    data = simple_imp.fit_transform(data)

    dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(dates))
    if request.query:
        feature = int(request.query.feature)

    choosed_df = dataframe[feature]
    y = choosed_df.values
    fourier_output = np.abs(fft.fft(y))
    frecuencies = fft.fftfreq(len(y))

    xmaxes = frecuencies[np.argpartition(fourier_output[2:], -6)[-6:]]
    xmaxes = 1/xmaxes[xmaxes > 0]
    periods = (xmaxes / 30).astype('int')

    periods = periods[(periods > 1) & (periods < 13)]

    return { "periods": np.unique(periods).tolist(),
             "timespan": str(periods[0]) }


@route('/src/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./src')


bottle.run(reloader=True, debug=True, port=8081)
