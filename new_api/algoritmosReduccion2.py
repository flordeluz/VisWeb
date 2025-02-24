# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA, FactorAnalysis
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import MinMaxScaler #, MaxAbsScaler
from factor_analyzer import calculate_kmo

# Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time

# Array of results
res_threads = []


# MinMax fraction testing scale
mmx_fs = 1 / 1000

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
    res_threads.append({"message": f"Pearson Dim.Reduction={to_drop}", "status": correlacion})
    return correlacion, to_drop


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
    res_threads.append({"message": f"Spearman Dim.Reduction={to_drop}", "status": correlacion})
    return correlacion, to_drop


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
    res_threads.append({"message": f"Kendall Dim.Reduction={to_drop}", "status": correlacion})
    return correlacion, to_drop

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
    features_to_drop = high_vif["Feature"].to_list()
    if len(high_vif) > 0:
        multicollinearity = True
        #
    print("[ Multicollinearity Variance Factor Inflation:", high_vif["VIF"].to_numpy(), "]")
    print("[ Multicollinearity Features:", features_to_drop, "]")
    print("[ Multicollinearity Detected:", multicollinearity, "]")
    res_threads.append({"message": f"Multicollinearity Dim.Reduction={features_to_drop}", "status": multicollinearity})
    return multicollinearity, features_to_drop


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


def choose_dimensionality_reduction(X):
    data = X.copy()
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"])
        data = data.set_index("date")
        #
    print(data)
    # mm = MinMaxScaler(feature_range=(0 + mmx_fs, 1 + mmx_fs))
    # data[list(data.columns)] = mm.fit_transform(data[list(data.columns)])
    # print(data)
    data = data.loc[:, data.std() > 0]
    print(data)
    kmo_all, kmo_overall = calculate_kmo(data)
    print(f"[ KMO Overall Score: {kmo_overall:.4f} ]")
    if kmo_overall >= 0.7:
        return "Factor Analysis"
    else:
        return "PCA and correlation"


# Crear un array con las funciones
array_funciones = [ verificar_correlacion_pearson,
                    verificar_correlacion_spearman,
                    verificar_correlacion_kendall,
                    check_multicollinearity,
                    check_dimensionality_reduction_pca,
                    check_dimensionality_reduction_fa ]


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
        check_multicollinearity(dataframe)
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
    print("[ REDUCTION TESTS:", val_positivos, "OUT OF", analyzed, "ARE POSITIVE. ]")
    # >= 50%, positive
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
