# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.preprocessing import MinMaxScaler

# Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time

# Array of results
res_threads = []


# MinMax fraction testing scale
mmx_fs = 1 / 1000


def outliers_sufficiency_test(X, z_threshold = 1.96):
    dataframe = X.copy()
    if "date" in dataframe.columns:
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe = dataframe.set_index("date")
        #
    for feature in dataframe.columns:
        serie = dataframe[feature]
        mean = np.mean(serie)
        sd = np.std(serie, ddof=1)
        z_scores = np.abs((serie - mean) / sd)
        serie[z_scores > z_threshold] = np.median(serie)
        #
    outlier = False
    for feature in dataframe.columns:
        serie = dataframe[feature]
        q1 = np.percentile(serie, 25)
        q3 = np.percentile(serie, 75)
        iqr = q3 - q1
        # Calcular los límites de los valores atípicos
        lim_inf = q1 - 1.5 * iqr
        lim_sup = q3 + 1.5 * iqr
        valores_atipicos = serie[(serie < lim_inf) | (serie > lim_sup)]
        num_valores_atipicos = len(valores_atipicos)
        if num_valores_atipicos > 0:
            outlier = True
            break
        #
    if outlier:
        return "Interquartile Range"
    else:
        return "Z-Score"


def obtener_ruido_de(X, umbral = 5):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    dataframe = X
    ruido = False
    for feature in dataframe.columns:
        serie = list(dataframe[feature])
        media = np.mean(serie)
        desv_std = np.std(serie)
        # Calculamos los límites superior e inferior
        lim_sup = media + umbral * desv_std
        lim_inf = media - umbral * desv_std
        # Identificamos los puntos de la serie que están fuera del umbral
        puntos_ruidosos = [punto for punto in serie if punto > lim_sup or punto < lim_inf]
        if (len(puntos_ruidosos) != 0): 
            ruido = True
            break
        #
    print("[ Standard Deviation Noise Detected:", ruido, "]")
    res_threads.append({"message": "Standard Deviation Noise Detected", "status": ruido})
    return ruido


def obtener_ruido_cv(X, threshold = 2):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # dataframe = X
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    ruido = False
    print("[ DATA FRAME ]\n", dataframe)
    for feature in dataframe.columns:
        serie = list(dataframe[feature])
        media = np.mean(serie)
        desviacion_estandar = np.std(serie)
        try:
            coeficiente_de_variacion = desviacion_estandar / media
        except FloatingPointError as e:
            print("[ WEIRD MEAN ]:", feature, media)
            print("[ ERR ]:", e)
            continue
        if coeficiente_de_variacion > threshold:
            ruido = True
            break
        #
    print("[ Coefficient Variation Noise Detected:", ruido, "]")
    res_threads.append({"message": "Coefficient Variation Noise Detected", "status": ruido})   
    return ruido


def obtener_outlier_iqr(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    dataframe = X
    outlier = False
    for feature in dataframe.columns:
        serie = dataframe[feature]
        q1 = np.percentile(serie, 25)
        q3 = np.percentile(serie, 75)
        iqr = q3 - q1
        # Calcular los límites de los valores atípicos
        lim_inf = q1 - 1.5 * iqr
        lim_sup = q3 + 1.5 * iqr
        print("[[Feature, q1, q3, IQR ]]:", feature, q1, q3, iqr)
        print("[[Feature, Lower, Upper]]:", feature, lim_inf, lim_sup)
        print("[[Feature, Min,   Max  ]]:", feature, serie.min(), serie.max())
        valores_atipicos = serie[(serie < lim_inf) | (serie > lim_sup)]
        num_valores_atipicos = len(valores_atipicos)
        if num_valores_atipicos > 0:
            outlier = True
            break
        #
    print("[ Interquartile Range Outliers Detected:", outlier, "]")
    res_threads.append({"message": "Interquartile Range Outliers Detected", "status": outlier})
    return outlier


# z_threshold possible values (1.96, 2, 2.5, 3, 3.5)
def obtener_outlier_zscore(X, z_threshold = 3.5):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    dataframe = X
    outlier = False
    for feature in dataframe.columns:
        serie = dataframe[feature]
        mean = np.mean(serie)
        sd = np.std(serie, ddof=1)
        # Calcular el Z-score
        z_scores = np.abs((serie - mean) / sd)
        # Identificar los outliers
        outliers = serie[z_scores > z_threshold]
        print("[[Feature, Outliers 1 n]]:", feature, np.sort(outliers)[0] if len(outliers) > 0 else np.nan, np.sort(outliers)[-1] if len(outliers) > 0 else np.nan)
        print("[[Feature, mean, median]]:", mean, np.median(serie))
        print("[[Feature, Min,  Max   ]]:", feature, serie.min(), serie.max())
        if len(outliers) > 0:
            outlier = True
            break
        #
    print("[ Z-score Outliers Detected:", outlier, "]")
    res_threads.append({"message": "Z-score Outliers Detected", "status": outlier})
    return outlier


# Definir la prueba de Grubbs para el outlier máximo
def grubbs_max_test(data, alpha):
    n = len(data)
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    G_max = (np.max(data) - mean) / std_dev
    t_dist = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    numerator = (n - 1) * t_dist
    denominator = np.sqrt(n) * np.sqrt(n - 2 + t_dist**2)
    G_critical = numerator / denominator
    return G_max > G_critical, G_max


# Definir la prueba de Grubbs para el outlier mínimo
def grubbs_min_test(data, alpha):
    n = len(data)
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    G_min = (mean - np.min(data)) / std_dev
    t_dist = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    numerator = (n - 1) * t_dist
    denominator = np.sqrt(n) * np.sqrt(n - 2 + t_dist**2)
    G_critical = numerator / denominator
    return G_min > G_critical, G_min


# alpha possible values (0.01, 0.05, 0.10)
def obtener_outlier_grubbs(X, alpha = 0.01):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    dataframe = X
    outlier = False
    for feature in dataframe.columns:
        serie = dataframe[feature]
        # Identificar los outliers
        outlier_detected = True
        try:
            max_test_result = grubbs_max_test(serie, alpha)
            min_test_result = grubbs_min_test(serie, alpha)
        except FloatingPointError as e:
            print("[ WEIRD STDV ]:", feature)
            print("[ ERR ]:", e)
            continue
        if (max_test_result or min_test_result):
            outlier = True
            break
        #
    print("[ Grubbs Outliers Detected:", outlier, "]")
    res_threads.append({"message": "Grubbs Outliers Detected", "status": outlier})
    return outlier 


# Crear un array con las funciones
array_funciones = [ obtener_ruido_de, obtener_ruido_cv, obtener_outlier_iqr,
                    obtener_outlier_zscore, obtener_outlier_grubbs ]


# Creacion de funciones multihilo
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()
    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()


def comprobarLimpieza(dataframe, par = True):
    if par:
        ejecutarFuncionesMultihilo(dataframe, array_funciones)
        #
    else:
        obtener_ruido_de(dataframe)
        obtener_ruido_cv(dataframe)
        obtener_outlier_iqr(dataframe)
        obtener_outlier_zscore(dataframe)
        obtener_outlier_grubbs(dataframe)
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
    print("[ CLEANING TESTS:", val_positivos, "OUT OF", analyzed, "ARE POSITIVE. ]")
    # >= 50%, positive
    if val_positivos >= (analyzed*50/100):
        return True, messages
    else:
        return False, messages
