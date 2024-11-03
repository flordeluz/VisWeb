# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import r2_score
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss
import scipy.stats as stats
from sklearn.svm import LinearSVR
from sklearn.metrics import mean_squared_error
from sklearn.decomposition import FactorAnalysis
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import RFE
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import MinMaxScaler #, MaxAbsScaler

# Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time
# import sys

# Definir un diccionario compartido para almacenar los resultados
res_threads = []


# Definir MinMax fraction scale
mmx_fs = 1 / 1000
# mmx_fs = sys.float_info.epsilon

# CORRELACION ENTRE VARIABLES

def verificar_correlacion_pearson(X, threshold = 0.8):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # sc = MaxAbsScaler()
    df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    correlacion = False
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool_))
    to_drop = [column for column in upper.columns if any(upper[column] >= threshold)]
    if len(to_drop) > 0:
        correlacion = True
        #
    print("[ Pearson Highly Correlated Columns:", to_drop, "]")
    print("[ Pearson Correlation Detected:", correlacion, "]")
    res_threads.append({"message": "Pearson Correlation Detected", "status": correlacion})
    return correlacion


def verificar_correlacion_spearman(X, threshold = 0.8):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # sc = MaxAbsScaler()
    df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    correlacion = False
    corr_matrix = df.corr(method="spearman").abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool_))
    to_drop = [column for column in upper.columns if any(upper[column] >= threshold)]
    if len(to_drop) > 0:
        correlacion = True
        #
    print("[ Spearman Highly Correlated Columns:", to_drop, "]")
    print("[ Spearman Correlation Detected:", correlacion, "]")
    res_threads.append({"message": "Spearman Correlation Detected", "status": correlacion})
    return correlacion


def verificar_correlacion_kendall(X, threshold = 0.8):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # sc = MaxAbsScaler()
    df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    correlacion = False
    corr_matrix = df.corr(method="kendall").abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool_))
    to_drop = [column for column in upper.columns if any(upper[column] >= threshold)]
    if len(to_drop) > 0:
        correlacion = True
        #
    print("[ Kendall Highly Correlated Columns:", to_drop, "]")
    print("[ Kendall Correlation Detected:", correlacion, "]")
    res_threads.append({"message": "Kendall Correlation Detected", "status": correlacion})
    return correlacion

# LINEALIDAD

def check_multicollinearity(X, threshold=10):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # sc = MaxAbsScaler()
    df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    multicollinearity = False
    # Create a DataFrame to hold VIF values
    vif_data = pd.DataFrame()
    vif_data["Feature"] = df.columns
    if df.shape[1] > 1:
        vif_data["VIF"] = [variance_inflation_factor(df.values, i) for i in range(df.shape[1])]
    else:
        vif_data["VIF"] = [threshold for i in range(df.shape[1])]
        #
    high_vif = vif_data[vif_data["VIF"] > threshold]
    if len(high_vif) > 0:
        multicollinearity = True
        #
    print("[ Multicollinearity Variance Factor Inflation:", high_vif["VIF"].to_numpy(), "]")
    print("[ Multicollinearity Features:", high_vif["Feature"].to_numpy(), "]")
    print("[ Multicollinearity Detected:", multicollinearity, "]")
    res_threads.append({"message": "Multicollinearity Detected", "status": multicollinearity})
    return multicollinearity, high_vif["Feature"].to_numpy()


# def verificar_linealidad(X, threshold = 0.8):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     corr_matrix = df.corr().abs()
#     upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool_))
#     # Verifica si todas las correlaciones están por encima del umbral
#     is_linear = all(upper[upper.notnull()] > threshold)
#     print("[ Linearity Correlation Detected:", is_linear, "]")
#     res_threads.append({"message": "Linearity Correlation Detected", "status": is_linear})
#     return is_linear


# def verificar_linealidad_regression(X, threshold = 0.8):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     cantidad_true = 0
#     es_lineal = False
#     for i in range(len(df.columns)):
#         for j in range(i+1, len(df.columns)):
#             model = LinearRegression()
#             X = df.iloc[:, i].values.reshape(-1, 1)
#             y = df.iloc[:, j].values.reshape(-1, 1)
#             model.fit(X, y)
#             y_pred = model.predict(X)
#             r2 = r2_score(y, y_pred)
#             if r2 > threshold:
#                 cantidad_true += 1
#                 #
#     if cantidad_true >= len(df.columns)-1:
#         # Si todos los modelos tienen un R-score > umbral, True
#         es_lineal = True
#         #
#     print("[ Linear Regression Detected:", es_lineal, "]")
#     res_threads.append({"message": "Linear Regression Detected", "status": es_lineal})
#     return es_lineal


# def verificar_linealidad_pca(X, threshold = 0.8):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     X_scaled = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     pca = PCA(n_components = X_scaled.shape[1], random_state = 13)
#     pca.fit(X_scaled)
#     # Linear if variance of the first component > threshold
#     is_linear = pca.explained_variance_ratio_[0] > threshold
#     print("[ PCA Linearity Detected:", is_linear, "]")
#     res_threads.append({"message": "PCA Linearity Detected", "status": is_linear})
#     return is_linear


# def verificar_linealidad_acf(X, threshold = 0.2):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     cantidad_true = 0
#     es_lineal = False
#     for column in df.columns:
#         lag = int(min(10 * np.log10(df[column].count()), df[column].count() - 1))
#         autocorrelation = acf(df[column], nlags=lag, fft=False)[lag]
#         # Si la autocorrelación para el lag > threshold, False
#         if abs(autocorrelation) <= threshold:
#             cantidad_true += 1
#             #
#     if cantidad_true >= len(df.columns)-1:
#         es_lineal = True
#         #
#     print("[ ACF Linearity Detected:", es_lineal, "]")
#     res_threads.append({"message": "ACF Linearity Detected", "status": es_lineal})
#     return es_lineal


# def verificar_linealidad_pacf(X, threshold = 0.2):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     cantidad_true = 0
#     es_lineal = False
#     for column in df.columns:
#         lag = int(min(10 * np.log10(df[column].count()), df[column].count() // 2 - 1))
#         partial_autocorrelation = pacf(df[column], nlags=lag)[lag]
#         # Si la autocorrelación parcial para el lag > threshold, False
#         if abs(partial_autocorrelation) <= threshold:
#             cantidad_true += 1
#             #
#     if cantidad_true >= len(df.columns)-1:
#         es_lineal = True
#         #
#     print("[ PACF Linearity Detected:", es_lineal, "]")
#     res_threads.append({"message": "PACF Linearity Detected", "status": es_lineal})
#     return es_lineal

# ESTACIONARIEDAD

# def verificar_estacionariedad_adf(X, significance_level = 0.05):
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
#         try:
#             result = adfuller(df[column])
#         except ValueError as e:
#             print("[ FEATURE DATA POINT ]:", column)
#             print("[ ERR ]:", e)
#             continue
#         if result[1] >= significance_level:  # adf p-value >= 0.05
#             stationary = False
#             print("[", column, "is not stationary, ADF p-value:", result[1], "]")
#             break
#         #
#     print("[ Dickey-Fuller Stationarity Test:", stationary, "]")
#     res_threads.append({"message": "Dickey-Fuller Stationarity Test", "status": stationary})
#     return stationary


# def verificar_estacionariedad_kpss(X, significance_level = 0.05):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     df = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     stationary = True
#     for column in df.columns:
#         statistic, p_value, n_lags, critical_values = kpss(df[column])
#         if p_value < significance_level:  # kpss p-value < 0.05
#             stationary = False
#             print("[", column, "is not stationary, KPSS p-value:", p_value, "]")
#             break
#         #
#     print("[ KPSS Stationarity Test:", stationary, "]")
#     res_threads.append({"message": "KPSS Stationarity Test", "status": stationary})
#     return stationary

# ESTABILIDAD, SE COMPLEMENTA Y NECESITA CON ESTACIONARIEDAD

# def verificar_estabilidad_descomposicion(X, threshold = 0.1):
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     data = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     es_estable = False
#     cantidad_true = 0
#     for column in data.columns:
#         decomposed = seasonal_decompose(data[column], period=1, model="additive", extrapolate_trend="freq")
#         tendencia_var = np.var(decomposed.trend[np.isfinite(decomposed.trend)])
#         estacionalidad_var = np.var(decomposed.seasonal[np.isfinite(decomposed.seasonal)])
#         if tendencia_var < threshold or estacionalidad_var < threshold:
#             cantidad_true += 1
#             #
#     if cantidad_true >= len(data.columns)-1:
#         es_estable = True
#         #
#     print("[ Decomposition Stability Test:", es_estable, "]")
#     res_threads.append({"message": "Decomposition Stability Test", "status": es_estable})
#     return es_estable


# def verificar_estabilidad_lsvr(X, window_size = 3/4):
#     # NANS NOT ALLOWED
#     if "date" in X.columns:
#         X["date"] = pd.to_datetime(X["date"])
#         X = X.set_index("date")
#         #
#     sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
#     # sc = MaxAbsScaler()
#     data = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
#     is_stable = False
#     cantidad_true = 0
#     dv10 = 10**10
#     for column in data.columns:
#         series = data[column]
#         serwnd = int(len(series)*window_size)
#         train = series[:serwnd]
#         test = series[serwnd:]
#         model = LinearSVR(dual=False, loss="squared_epsilon_insensitive")
#         # model.fit(train.index.values.reshape(-1, 1), train.values)
#         model.fit((train.index.values.astype("datetime64[ns]").astype(np.timedelta64) / np.timedelta64(1, "s") / dv10).reshape(-1, 1), train.values)
#         # predictions = model.predict(test.index.values.reshape(-1, 1))
#         predictions = model.predict((test.index.values.astype("datetime64[ns]").astype(np.timedelta64) / np.timedelta64(1, "s") / dv10).reshape(-1, 1))
#         mse = mean_squared_error(test.values, predictions)
#         # MSE < umbral, estable
#         if mse < 0.1:
#             cantidad_true += 1
#             #
#     if cantidad_true >= len(data.columns)-1:
#         is_stable = True
#         #
#     print("[ Linear Support-Vector-Regression Stability Test:", is_stable, "]")
#     res_threads.append({"message": "Linear Support-Vector-Regression Stability Test", "status": is_stable})
#     return is_stable

# REDUCCION DE DIMENSIONALIDAD

def check_dimensionality_reduction_pca(X, threshold = 0.9):
    # UNSCALED DATA
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    X_scaled = X
    # sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # # sc = MaxAbsScaler()
    # X_scaled = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    pca = PCA(n_components = X_scaled.shape[1], random_state = 13)
    pca.fit(X_scaled)
    cumulative_variance_ratio = pca.explained_variance_ratio_.cumsum()
    # cumulative_variance_ratio_threshold = cumulative_variance_ratio >= threshold
    cumulative_variance_ratio_threshold = cumulative_variance_ratio < threshold
    print("[ PCA Variance Ratio:", cumulative_variance_ratio, "]")
    print("[ PCA Var.Ratio Trsh:", cumulative_variance_ratio_threshold, "]")
    result = np.any(cumulative_variance_ratio_threshold)
    print("[ PCA Dim.Reduction:", result, "]")
    res_threads.append({"message": "PCA Dim.Reduction", "status": result})
    return result


def check_dimensionality_reduction_fa(X, factor_count = 1, threshold = 0.4):
    # UNSCALED DATA
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    data = X
    # sc = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # # sc = MaxAbsScaler()
    # data = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    model = FactorAnalysis(n_components=factor_count)
    model.fit(data)
    factor_loadings = model.components_[0]
    print("[ FA Dim.Reduction Loadings:", factor_loadings, "]")
    features_to_drop = [data.columns[i] for i, value in enumerate(factor_loadings) if abs(value) < threshold]
    result = len(features_to_drop) > 0
    print("[ FA Dim.Reduction Features: ", features_to_drop, "]")
    print("[ FA Dim.Reduction Detected: ", result, "]")
    # print(f"[ FA Dim.Reduction={features_to_drop}", result, "]")
    res_threads.append({"message": f"FA Dim.Reduction={features_to_drop}", "status": result})
    return result, features_to_drop

# Crear un array con las funciones
array_funciones = [ verificar_correlacion_pearson, verificar_correlacion_spearman,
                    verificar_correlacion_kendall, # verificar_linealidad, verificar_linealidad_regression,
                    check_multicollinearity, # verificar_linealidad_pca,
                    # verificar_linealidad_acf, verificar_linealidad_pacf,
                    # verificar_estacionariedad_adf, verificar_estacionariedad_kpss,
                    # verificar_estabilidad_descomposicion, verificar_estabilidad_lsvr,
                    check_dimensionality_reduction_pca, check_dimensionality_reduction_fa ]


# CREACION DE FUNCIONES MULTIHILO
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()
    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()


def comprobarReduccion(dataframe, par = True):
    if par:
        ejecutarFuncionesMultihilo(dataframe, array_funciones)
        #
    else:
        verificar_correlacion_pearson(dataframe)
        verificar_correlacion_spearman(dataframe)
        verificar_correlacion_kendall(dataframe)
        # verificar_linealidad(dataframe)
        # verificar_linealidad_regression(dataframe)
        check_multicollinearity(dataframe)
        # verificar_linealidad_pca(dataframe)
        # verificar_linealidad_acf(dataframe)
        # verificar_linealidad_pacf(dataframe)
        # verificar_estacionariedad_adf(dataframe)
        # verificar_estacionariedad_kpss(dataframe)
        # verificar_estabilidad_descomposicion(dataframe)
        # verificar_estabilidad_lsvr(dataframe)
        check_dimensionality_reduction_pca(dataframe)
        check_dimensionality_reduction_fa(dataframe)
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
    print("[ Algoritmos Reduccion", val_positivos, "de", analyzed, "son positivos. ]")
    # Si el 50% de los algoritmos son True, retornar
    if val_positivos >= (analyzed*50/100):
        return True, messages
    else:
        return False, messages


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
