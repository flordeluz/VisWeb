# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss
import matplotlib.pyplot as plt
from hurst import compute_Hc
from sklearn.preprocessing import MaxAbsScaler

#Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time

# Definir un diccionario compartido para almacenar los resultados
res_threads = []


def obtener_no_estacionariedad_adf(X, significance_level = 0.05):
    # NANS NOT ALLOWED
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    stationary = True
    for column in df.columns:
        result = adfuller(df[column])
        if result[1] >= significance_level:  # adf p-value >= 0.05
            stationary = False
            print("[", column, "is not stationary, ADF p-value:", result[1], "]")
            break
        #
    print("[ Dickey-Fuller Non-stationarity Test:", not stationary, "]")
    res_threads.append({"message": "Dickey-Fuller Non-stationarity Test", "status": not stationary})
    return not stationary


def obtener_no_estacionariedad_kpss(X, significance_level = 0.05):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    stationary = True
    for column in df.columns:
        statistic, p_value, n_lags, critical_values = kpss(df[column])
        if p_value < significance_level:  # kpss p-value < 0.05
            stationary = False
            print("[", column, "is not stationary, KPSS p-value:", p_value, "]")
            break
        #
    print("[ KPSS Non-stationarity Test:", not stationary, "]")
    res_threads.append({"message": "KPSS Non-tationarity Test", "status": not stationary})
    return not stationary


def obtener_comportamiento_persistente_hurst(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    persistent = False
    for feature in dataframe.columns:
        data = dataframe[feature]
        # Calcular la dimensión fractal de Hurst
        H, c, data = compute_Hc(data, simplified=True)
        # Determinar si la serie temporal es lineal o no lineal
        if H > 0.5:
            persistent = True
            break
        #
    print("[ Hurst Persistent Behavior Detected:", persistent, "]")
    res_threads.append({"message": "Hurst Persistent Behavior Detected", "status": persistent})
    return persistent


# Crear un array con las funciones
array_funciones = [ obtener_no_estacionariedad_adf, obtener_no_estacionariedad_kpss,
                    obtener_comportamiento_persistente_hurst ] 


#CREACION DE FUNCIONES MULTIHILO
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()
    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()

    
def comprobarTransformacion(dataframe, par = True):
    if par:
        ejecutarFuncionesMultihilo(dataframe, array_funciones)
        #
    else:
        obtener_no_estacionariedad_adf(dataframe)
        obtener_no_estacionariedad_kpss(dataframe)
        obtener_comportamiento_persistente_hurst(dataframe)
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
    print("[ Algoritmos Transformacion", val_positivos, "de", analyzed, "son positivos. ]")
    # Si el 50% de los algoritmos son True, retornar
    if val_positivos >= (analyzed*50/100):
        return True, messages
    else:
        return False, messages
