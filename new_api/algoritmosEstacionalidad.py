# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import io
import base64
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pywt import cwt
from statsmodels.tsa.stattools import acf, pacf, q_stat
from scipy.fftpack import fft
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MaxAbsScaler

# Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time

# Definir un diccionario compartido para almacenar los resultados
res_threads = []


def seasonality_detection(ds, cols_list):
    # reshtml = '<p style="text-align:center"><h5><b>Estacionalidad</b></h5></p>'
    reshtml = ''
    pltid = 1
    rows = len(cols_list)
    plt.figure(figsize = (9, 6), dpi = 100)
    _, ax = plt.subplots(rows, 1)
    for coln in cols_list:
        decomp = seasonal_decompose(ds[coln], period=1, model="additive", extrapolate_trend="freq")
        seasonal = decomp.seasonal
        ax = plt.subplot(rows, 1, pltid)
        ax.plot(seasonal, label=coln, marker='.', markersize=1)
        ax.legend(loc='upper left')
        pltid += 1
        #
    plt.tight_layout()
    s = io.BytesIO()
    plt.savefig(s, format="png", bbox_inches="tight")
    plt.close()
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    reshtml += '<img src="data:image/png;base64,%s">' % s
    return reshtml


def trend_detection(ds, cols_list):
    # reshtml = '<p style="text-align:center"><h5><b>Tendencia</b></h5></p>'
    reshtml = '';
    pltid = 1
    rows = len(cols_list)
    plt.figure(figsize = (9, 6), dpi = 100)
    _, ax = plt.subplots(rows, 1)
    for coln in cols_list:
        decomp = seasonal_decompose(ds[coln], period=1, model="additive", extrapolate_trend="freq")
        trend = decomp.trend
        ax = plt.subplot(rows, 1, pltid)
        ax.plot(trend, label=coln, marker='.', markersize=1)
        ax.legend(loc='upper left')
        pltid += 1
        #
    plt.tight_layout()
    s = io.BytesIO()
    plt.savefig(s, format="png", bbox_inches="tight")
    plt.close()
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    reshtml += '<img src="data:image/png;base64,%s">' % s
    return reshtml


# PERIODICIDAD

# def check_box_pierce(data, alpha = 0.05):
#     # Calcula la ACF
#     acf_values, confint = acf(data, nlags=len(data), alpha=alpha)
#     # Realiza la prueba de Box-Pierce
#     q_stat_values, p_values = q_stat(acf_values, len(data))
#     return np.any(p_values < alpha)


# def verificar_box_pierce(X):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MaxAbsScaler()
#     dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     is_periodic = False
#     cantidad_true = 0
#     for feature in dataframe.columns:
#         if check_box_pierce(dataframe[feature]):
#             cantidad_true += 1
#             #
#     if cantidad_true >= len(dataframe.columns)-1:
#         is_periodic = True
#         #
#     print("[ Box-Pierce Periodic Test:", is_periodic, "]")
#     res_threads.append({"message": "Box-Pierce Periodic Test", "status": is_periodic})
#     return is_periodic


def check_box_pierce2(data, alpha = 0.05):
    # Realiza la prueba de Box-Pierce
    result = acorr_ljungbox(data)
    # La serie temporal es "periódica" si el valor p es menor que el nivel de significancia
    return any(p < alpha for p in result["lb_pvalue"])


def verificar_box_pierce2(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    is_periodic = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_box_pierce2(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        is_periodic = True
        #
    print("[ Box-Pierce-2 Periodic Test:", is_periodic, "]")
    res_threads.append({"message": "Box-Pierce-2 Periodic Test", "status": is_periodic})
    return is_periodic


def check_periodicity_fft(series, threshold = 1e4):
    series_array = series.values
    spectrum = fft(series_array)
    # Calcula la potencia del espectro
    power = np.abs(spectrum)
    # Retorna si existe alguna potencia espectral por encima del umbral
    return np.any(power[1:] > threshold)


def verificar_periodicidad_fft(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    is_periodic = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_periodicity_fft(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        is_periodic = True
        #
    print("[ FFT Periodic Test:", is_periodic, "]")
    res_threads.append({"message": "FFT Periodic Test", "status": is_periodic})
    return is_periodic


def check_periodicity_fft2(data):
    data = data.values
    fft_vals = fft(data)
    # Calcula las frecuencias absolutas
    fft_abs = np.abs(fft_vals)
    # Encuentra la frecuencia con la amplitud máxima
    peak_frequency = np.argmax(fft_abs[1:]) + 1
    # Asume que la serie es periódica si la amplitud máxima es significativamente mayor que la media
    return fft_abs[peak_frequency] > np.mean(fft_abs)


def verificar_periodicidad_fft2(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    is_periodic = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_periodicity_fft2(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        is_periodic = True
        #
    print("[ FFT-2 Periodic Test:", is_periodic, "]")
    res_threads.append({"message": "FFT-2 Periodic Test", "status": is_periodic})
    return is_periodic


def check_periodicity_fft3(data):
    data = data.values
    yf = fft(data)
    # Calcula las frecuencias absolutas
    abs_yf = 2.0/len(data) * np.abs(yf[0:len(data)//2])
    # Encuentra la frecuencia con la amplitud máxima
    peak_frequency = np.argmax(abs_yf[1:]) + 1
    # Asume que la serie es periódica si la amplitud máxima es significativamente mayor que la media
    return abs_yf[peak_frequency] > np.mean(abs_yf)


def verificar_periodicidad_fft3(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    is_periodic = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_periodicity_fft3(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        is_periodic = True
        #
    print("[ FFT-3 Periodic Test:", is_periodic, "]")
    res_threads.append({"message": "FFT-3 Periodic Test", "status": is_periodic})
    return is_periodic


def check_periodicity_acf_pacf(series, threshold = 0.5):
    autocorrelation = acf(series)
    partial_autocorrelation = pacf(series)
    return max(abs(autocorrelation[1:])) > threshold or max(abs(partial_autocorrelation[1:])) > threshold


def verificar_periodicidad_acf_pacf(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    is_periodic = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_periodicity_acf_pacf(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        is_periodic = True
        #
    print("[ ACF-PACF Periodic Test:", is_periodic, "]")
    res_threads.append({"message": "ACF-PACF Periodic Test", "status": is_periodic})
    return is_periodic


def check_wavelet_periodicity(series, threshold = 0.5):
    cwtmatr, freqs = cwt(series, np.arange(1, 30), "morl")
    max_coef = np.max(np.abs(cwtmatr))
    return max_coef > threshold


def verificar_periodicidad_wavelet(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    is_periodic = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_wavelet_periodicity(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        is_periodic = True
        #
    print("[ Wavelet Periodic Test:", is_periodic, "]")
    res_threads.append({"message": "Wavelet Periodic Test", "status": is_periodic})
    return is_periodic

# ESTACIONALIDAD

def check_seasonal_periodicity(series, expected_lag, threshold = 0.5):
    # Aplica STL a la serie
    result = STL(series, period=expected_lag).fit()
    # Calcula la ACF de la componente estacional
    acf_values = acf(result.seasonal, fft=False, nlags=len(series))
    # Verifica si la autocorrelación en el desfase esperado es mayor que el umbral
    return abs(acf_values[expected_lag]) > threshold


def verificar_descomposiocion_stl(X, expected_lag = 12):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_seasonality = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_seasonal_periodicity(dataframe[feature], expected_lag):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_seasonality = True
        #
    print("[ ACF Seasonality Test:", has_seasonality, "]")
    res_threads.append({"message": "ACF Seasonality Test", "status": has_seasonality})
    return has_seasonality


def fisher_seasonality_test(data, alpha = 0.05):
    n = len(data)
    acf_vals = acf(data, nlags=n-1, fft=True)  # cálculo de la función de autocorrelación
    acf_vals_sq = np.square(acf_vals[1:])  # eleva al cuadrado los valores de la ACF
    # cálculo de las medias móviles para diferentes tamaños de ventana
    mean_vals = [np.mean(acf_vals_sq[i+1:n]) if len(acf_vals_sq[i+1:n]) > 0 else np.nan for i in range(n-1)]
    # cálculo de la varianza de las medias móviles
    var_mean = np.var(mean_vals, ddof=1)  # ajuste ddof=1 para calcular la varianza muestral
    # cálculo del estadístico de prueba
    fisher_statistic = (n-1) * var_mean / np.mean(acf_vals_sq[1:])
    # cálculo del valor crítico de Fisher
    fisher_critical_value = 1.0 / alpha
    # comparación del estadístico de prueba con el valor crítico
    return fisher_statistic > fisher_critical_value


def verificar_estacionalidad_fisher(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_seasonality = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if fisher_seasonality_test(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_seasonality = True
        #
    print("[ Fisher Seasonality Test:", has_seasonality, "]")
    res_threads.append({"message": "Fisher Seasonality Test", "status": has_seasonality})
    return has_seasonality

# AMPLITUD

def check_amplitude(series, threshold = 0.5):
    # Realiza la descomposición estacional
    result = seasonal_decompose(series, period=1, model="additive")
    # Obtiene la amplitud de la estacionalidad (la diferencia entre el máximo y el mínimo)
    amplitude = result.seasonal.max() - result.seasonal.min()
    # Retorna si la amplitud supera el umbral
    return amplitude > threshold


def verificar_amplitud(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_amplitude = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_amplitude(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_amplitude = True
        #
    print("[ Decomposition Amplitude Test:", has_amplitude, "]")
    res_threads.append({"message": "Decomposition Amplitude Test", "status": has_amplitude})
    return has_amplitude


def check_amplitude_fft(series, threshold = 0.5):
    n = len(series)
    # Aplicar la Transformada rápida de Fourier
    yf = fft(series.values)
    xf = np.linspace(0.0, 1.0/(2.0*1), n//2)
    # Excluir la frecuencia cero y obtener la amplitud máxima
    amplitudes = 2.0/n * np.abs(yf[0:n//2])
    max_amplitude = np.max(amplitudes[1:])
    # Verificar si la amplitud máxima supera el umbral
    return max_amplitude > threshold


def verificar_amplitud_fft(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_amplitude = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_amplitude_fft(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_amplitude = True
        #
    print("[ FFT Amplitude Test:", has_amplitude, "]")
    res_threads.append({"message": "FFT Amplitude Test", "status": has_amplitude})
    return has_amplitude

# FRECUENCIA

def check_frequency_fft(series, threshold = 0.5):
    n = len(series)
    # Aplicar la Transformada Rápida de Fourier
    yf = fft(series.values)
    xf = np.linspace(0.0, 1.0/(2.0*1), n//2)
    # Excluir la frecuencia cero y obtener la frecuencia con la amplitud máxima
    amplitudes = 2.0/n * np.abs(yf[0:n//2])
    max_freq = xf[np.argmax(amplitudes[1:])]
    # Verificar si la frecuencia máxima supera el umbral
    return max_freq > threshold


def verificar_frecuencia_fft(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_frequency = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_frequency_fft(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_frequency = True
        #
    print("[ FFT Frequency Test:", has_frequency, "]")
    res_threads.append({"message": "FFT Frequency Test", "status": has_frequency})
    return has_frequency


def check_frequency_acf(series, threshold = 0.5):
    # Calcular la ACF de la serie
    autocorrelation = acf(series, nlags=len(series)//2, fft=True)
    # Ignorar el primer lag (correlación de la serie consigo misma)
    autocorrelation = autocorrelation[1:]
    # Encontrar el lag con la autocorrelación más alta
    max_lag = np.argmax(autocorrelation)
    max_autocorrelation = autocorrelation[max_lag]
    # Verificar si la autocorrelación máxima supera el umbral
    return max_autocorrelation > threshold


def verificar_frecuencia_acf(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_frequency = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if check_frequency_acf(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_frequency = True
        #
    print("[ ACF Frequency Test:", has_frequency, "]")
    res_threads.append({"message": "ACF Frequency Test", "status": has_frequency})
    return has_frequency

# DURACION
            
def determine_timespan(df, significance_level = 0.05):
    acf_values = acf(df, nlags=len(df)-1)
    for i in range(1, len(acf_values)):
        if acf_values[i] > significance_level:
            return True
        #
    return False


def verificar_duracion(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    has_timespan = False
    cantidad_true = 0
    for feature in dataframe.columns:
        if determine_timespan(dataframe[feature]):
            cantidad_true += 1
            #
    if cantidad_true >= len(dataframe.columns)-1:
        has_timespan = True
        #
    print("[ ACF Time Span Test:", has_timespan, "]")
    res_threads.append({"message": "ACF Time Span Test", "status": has_timespan})
    return has_timespan


# Crear un array con las funciones
array_funciones = [ # verificar_box_pierce,
                    verificar_box_pierce2, verificar_periodicidad_fft,
                    verificar_periodicidad_fft2, verificar_periodicidad_fft3,
                    verificar_periodicidad_acf_pacf, verificar_periodicidad_wavelet,
                    verificar_descomposiocion_stl, verificar_estacionalidad_fisher,
                    verificar_amplitud, verificar_amplitud_fft, verificar_frecuencia_fft,
                    verificar_frecuencia_acf, verificar_duracion ] 


# CREACION DE FUNCIONES MULTIHILO
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()
    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()

    
def comprobarEstacionalidad(dataframe, par = True):
    if par:
        ejecutarFuncionesMultihilo(dataframe, array_funciones)
        #
    else:
        # verificar_box_pierce(dataframe)
        verificar_box_pierce2(dataframe)
        verificar_periodicidad_fft(dataframe)
        verificar_periodicidad_fft2(dataframe)
        verificar_periodicidad_fft3(dataframe)
        verificar_periodicidad_acf_pacf(dataframe)
        verificar_periodicidad_wavelet(dataframe)
        verificar_descomposiocion_stl(dataframe)
        verificar_estacionalidad_fisher(dataframe)
        verificar_amplitud(dataframe)
        verificar_amplitud_fft(dataframe)
        verificar_frecuencia_fft(dataframe)
        verificar_frecuencia_acf(dataframe)
        verificar_duracion(dataframe)
        #
    val_positivos = 0
    messages = []
    analyzed = len(res_threads)
    for valor in res_threads:
        if valor["status"] == True: 
            val_positivos+=1
            messages.append(valor["message"])
            #
    res_threads.clear()
    print("[ Algoritmos Estacionalidad", val_positivos, "de", analyzed, "son positivos. ]")
    # Si el 50% de los algoritmos son True, retornar
    if val_positivos >= (analyzed*50/100): return True, messages
    else: return False, messages


# def tiemposDeEjecucion(df, arr_func):
#     for funcion in arr_func:
#         inicio = time.time()
#         funcion(df)
#         fin = time.time()
#         tiempo_ejecucion = fin - inicio
#         print(funcion)
#         print(f"Tiempo de ejecución: {tiempo_ejecucion} segundos")
#         print("")
#         res_threads.clear()
