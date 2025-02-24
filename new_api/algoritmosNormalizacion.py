# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import pandas as pd
import numpy as np
from numpy.linalg import LinAlgError
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from scipy.stats import gaussian_kde, norm, lognorm
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler, RobustScaler

# Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time

# Array of results
res_threads = []


# MinMax fraction testing scale
mmx_fs = 1 / 1000


def keep_correlation_test(X):
    dataframe = X.copy()
    if "date" in dataframe.columns:
        dataframe["date"] = pd.to_datetime(dataframe["date"])
        dataframe = dataframe.set_index("date")
        #
    ma_dataframe = dataframe.copy()
    ma = MaxAbsScaler()
    ma_dataframe[list(dataframe.columns)] = ma.fit_transform(ma_dataframe[list(dataframe.columns)])
    mm_dataframe = dataframe.copy()
    mm = MinMaxScaler()
    mm_dataframe[list(dataframe.columns)] = mm.fit_transform(mm_dataframe[list(dataframe.columns)])
    sc_dataframe = dataframe.copy()
    sc = StandardScaler()
    sc_dataframe[list(dataframe.columns)] = sc.fit_transform(sc_dataframe[list(dataframe.columns)])
    rb_dataframe = dataframe.copy()
    rb = RobustScaler()
    rb_dataframe[list(dataframe.columns)] = rb.fit_transform(rb_dataframe[list(dataframe.columns)])
    # Average target metrics
    avg_ma = 0
    avg_mm = 0
    avg_sc = 0
    avg_rb = 0
    for feature in dataframe.columns:
        # Original
        stl_df = STL(dataframe[feature]).fit()
        # Targets
        stl_ma = STL(ma_dataframe[feature]).fit()
        stl_mm = STL(mm_dataframe[feature]).fit()
        stl_sc = STL(sc_dataframe[feature]).fit()
        stl_rb = STL(rb_dataframe[feature]).fit()
        # MaxAbs
        cor_tre_ma = np.corrcoef(stl_df.trend, stl_ma.trend)[0, 1]
        cor_sea_ma = np.corrcoef(stl_df.seasonal, stl_ma.seasonal)[0, 1]
        avg_ma += (cor_tre_ma + cor_sea_ma) / 2
        # MinMax
        cor_tre_mm = np.corrcoef(stl_df.trend, stl_mm.trend)[0, 1]
        cor_sea_mm = np.corrcoef(stl_df.seasonal, stl_mm.seasonal)[0, 1]
        avg_mm += (cor_tre_mm + cor_sea_mm) / 2
        # Standard
        cor_tre_sc = np.corrcoef(stl_df.trend, stl_sc.trend)[0, 1]
        cor_sea_sc = np.corrcoef(stl_df.seasonal, stl_sc.seasonal)[0, 1]
        avg_sc += (cor_tre_sc + cor_sea_sc) / 2
        # Robust
        cor_tre_rb = np.corrcoef(stl_df.trend, stl_rb.trend)[0, 1]
        cor_sea_rb = np.corrcoef(stl_df.seasonal, stl_rb.seasonal)[0, 1]
        avg_rb += (cor_tre_rb + cor_sea_rb) / 2
        #
    avg_ma /= len(dataframe.columns)
    avg_mm /= len(dataframe.columns)
    avg_sc /= len(dataframe.columns)
    avg_rb /= len(dataframe.columns)
    corrls = { avg_ma: "MaxAbs", avg_mm: "MinMax", avg_sc: "Standard", avg_rb: "Robust" }
    print("[ Keep correlation test ]:", corrls)
    print("[ Keep correlation selected ]:", corrls[[sorted(corrls)[-1]]])
    return corrls[[sorted(corrls)[-1]]]


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
array_funciones = [ obtener_no_patrones_estacionalidad,
                    obtener_distribucion_conocida ]


# Creacion de funciones multihilo
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
    print("[ NORMALIZATION TESTS:", val_positivos, "OUT OF", analyzed, "ARE POSITIVE. ]")
    # >= 50%, positive
    if val_positivos >= (analyzed*50/100):
        return True, messages
    else:
        return False, messages

