# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import pandas as pd
import numpy as np
from numpy.linalg import LinAlgError
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from scipy.stats import gaussian_kde, norm, lognorm
from sklearn.preprocessing import MinMaxScaler #, MaxAbsScaler

#Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time
# import sys

# Definir un diccionario compartido para almacenar los resultados
res_threads = []


# Definir MinMax fraction scale
mmx_fs = 1 / 1000
# mmx_fs = sys.float_info.epsilon


# Stationarity does not guarantee normal distribution
# def obtener_estacionaria_mv(X, significance_level = 0.05):
#     # NANS NOT ALLOWED
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     stationary = True
#     for column in df.columns:
#         result = adfuller(df[column])
#         if result[1] >= significance_level:  # adf p-value >= 0.05
#             stationary = False
#             print("[", column, "is not stationary, ADF p-value:", result[1], "]")
#             break
#         #
#     print("[ Dickey-Fuller Stationarity Test:", stationary, "]")
#     res_threads.append({"message": "Dickey-Fuller Stationarity Test", "status": stationary})
#     return stationary


def obtener_no_patrones_estacionalidad(X, periodo = 12):
    # periodo: especifica el periodo de los datos ejm:datos diarios=365, semanal=52, mensual=12
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    seasonal = False
    for feature in dataframe.columns:
        decomposition = seasonal_decompose(dataframe[feature], model="additive", period=periodo)
        seasonal_variance = decomposition.seasonal.var()
        residual_variance = decomposition.resid.var()
        # verificar si hay patrones de estacionalidad
        if seasonal_variance > residual_variance:
            seasonal = True
            break
        #
    print("[ Seasonality affects distribution:", seasonal, "]")
    res_threads.append({"message": "Seasonality affects distribution", "status": seasonal})
    return seasonal


def obtener_distribucion_conocida(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    distConocida = False
    print("[ DATA FRAME ]\n", dataframe)
    for feature in dataframe.columns:
        series = dataframe[feature]
        try:
            pdf = gaussian_kde(series)
        except LinAlgError as e:
            print("[ FEATURE DATA POINTS TOO SIMILAR/COLLINEAR ]:", feature)
            print("[ ERR ]:", e)
            continue
        std = np.std(series)
        # Comparar la desviación estándar con la desviación estándar esperada para la distribución normal
        expected_std = norm.std(loc=0, scale=1)
        if abs(std - expected_std) < 0.05:
            distConocida = True
            break
        else:
            # Evaluar si la distribución coincide con alguna distribución conocida
            try:
                log_params = lognorm.fit(series)
                distConocida = True
                break
            except:
                distConocida = False
                #
    print("[ Data Not Normally Distributed:", not distConocida, "]")
    res_threads.append({"message": "Data Not Normally Distributed", "status": not distConocida})
    return not distConocida


# Crear un array con las funciones
array_funciones = [ # obtener_estacionaria_mv,
                    obtener_no_patrones_estacionalidad,
                    obtener_distribucion_conocida ]


#CREACION DE FUNCIONES MULTIHILO
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()
    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()


def comprobarNormalizacion(dataframe, par = True):
    if par:
        ejecutarFuncionesMultihilo(dataframe, array_funciones)
        #
    else:
        # obtener_estacionaria_mv(dataframe)
        obtener_no_patrones_estacionalidad(dataframe)
        obtener_distribucion_conocida(dataframe)
        #
    val_positivos = 0
    messages = []
    analyzed = len(res_threads)
    for valor in res_threads:
        if valor["status"] == True: 
            val_positivos += 1
            messages.append(valor["message"])
            #
    res_threads.clear()
    print("[ Algoritmos Normalizacion", val_positivos, "de", analyzed, "son positivos. ]")
    # Si el 50% de los algoritmos son True, retornar
    if val_positivos >= (analyzed*50/100):
        return True, messages
    else:
        return False, messages
