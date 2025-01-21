# Essential Libraries
from os import stat
import bottle
from bottle import request, response, route, static_file, view
import re
import json
import simplejson

from pandas.core.frame import DataFrame
from pandas.io.parsers import read_csv
import pandas as pd

import statsmodels.api as sm
import numpy as np
from matplotlib.pyplot import table
from scipy import fft
from scipy import signal as sig

from sklearn.decomposition import PCA
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
# from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler, StandardScaler

# HINT: Main Loader Class For Multiple Data Sources
# -------------------------------
from Dataloader.Mainloader import MainloaderClass
from Dataloader.GenLoader import GenLoader
# -------------------------------

# HINT: Data Transformation Testers Refactored
# -------------------------------
from helpers import get_period_days
from AlgoritmosLimpieza import comprobarLimpieza
from algoritmosNormalizacion import comprobarNormalizacion
from algoritmosTransformacion import comprobarTransformacion
from algoritmosReduccion2 import comprobarReduccion, check_dimensionality_reduction_fa
from algoritmosEstacionalidad import comprobarEstacionalidad, seasonality_detection, trend_detection, noise_detection
from algoritmosCiclicidad2 import comprobarCiclicidad, verificar_ciclo_fft
from algoritmosEstadisticas import describe_data, null_values_data, addinfo_data, corrmat_data, bivaran_data, boxplot_data
# -------------------------------

# HINT: Main Transformers Class For Data Transformation
# -------------------------------
from Dataredo.Mainredo import MainredoClass
from Dataredo.GenRedo import GenRedo
# -------------------------------

# # Parallel Execution Libraries
# import threading
# import concurrent.futures

# Shared Dictionary
resultados_threads = {}

# Loaders
# HINT: Main Loader Class For Data Sources
# -------------------------------
# DATA SOURCES MSG: A loop for reading folder names inside .data container
# DATA SOURCES MSG: will create path variables to be used as GenLoader
# DATA SOURCES MSG: objects derived from Mainloader Class.
ma_path = "./.data/Madrid/csvs_per_year/csvs_per_year/"
ml = GenLoader(ma_path)
in_path = "./.data/India/station_day.csv"
il = GenLoader(in_path)
pe_path = "./.data/Peru/"
aqpl = GenLoader(pe_path)
br_path = "./.data/Brasil/Data_AirQuality/"
bl = GenLoader(br_path)
# -------------------------------

# Scalers (Scale and Normalization)
# minmax_scaler = MinMaxScaler()
# sc_scaler = StandardScaler()

# Transformers
# HINT: Main Redo Class For Data Transformation
# -------------------------------
gr = GenRedo()
# -------------------------------

# Imputation For Completing Null Values
knn_imputer = KNNImputer(missing_values=-1, n_neighbors=10, weights="uniform")
simple_imp = SimpleImputer(missing_values=-1, strategy="mean")
iter_imp = IterativeImputer(missing_values=-1, max_iter=20)

# Objects, Classes, Functions, Methods, And Procedures
def enable_cors(fn):
    def wrapper(*args, **kwargs):
        bottle.response.set_header("Access-Control-Allow-Origin", "*")
        bottle.response.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        bottle.response.set_header("Access-Control-Allow-Headers", "Origin, Content-Type")

        # skip the function if it is not needed
        if bottle.request.method == "OPTIONS":
            return

        return fn(*args, **kwargs)
    return wrapper


loaders = {
    "madrid": ml,
    "aqp": aqpl,
    "india": il,
    "brasil": bl
}


response.headers["Content-Type"] = "application/json"

full_station_ds: DataFrame = None
current_df: DataFrame = None
aux_df: DataFrame = None
current_dataset = ""
current_station = ""
last_station = ""
init_state = False
dic = {}
# historial_df = {}
made_path = []


# Routers

@route("/meta_data/<dataset>")
@enable_cors
def meta_data(dataset):
    global init_state
    global made_path
    loader = loaders[dataset]
    loader.ds = loader.smo["raw"].copy()
    init_state = True
    made_path = []
    print(loader.ds.info())
    print(loader.ds)
    return json.dumps(loader.get_metadata())


# @route("/meta_data/<dataset>/<station>")
# @enable_cors
# def station_meta_data(dataset, station):
#     global last_station
#     loader = loaders[dataset]
#     station = station.upper()
#     print("[ pre-process last and current stations:", last_station, ",", station, "]")
#     if ("cache" not in loader.smo):
#         loader.smo["cache"] = dict()
#         #
#     if (last_station != "" & last_station in loader.smo["cache"]):
#         loader.smo = gr.station_auto_save(loader.smo, last_station)
#         #
#     loader.smo = gr.station_auto_init(loader.smo, station)
#     last_station = station
#     print("[ last station", last_station, "updated ]")
#     # return json.dumps(loader.get_station_metadata(station=station))
#     return json.dumps(loader.get_station_metadata(station))


@route("/data/<dataset>/<station>")
@enable_cors
def data(dataset, station):
    # global historial_df
    global full_station_ds
    global current_df
    global aux_df
    global last_station
    global init_state
    loader = loaders[dataset]
    station = station.upper()
    response.headers["Content-Type"] = "application/json"
    if init_state:
        print("[ pre-process last and current stations:", last_station, ",", station, "]")
        if ("cache" not in loader.smo):
            loader.smo["cache"] = dict()
            #
        if ((last_station != "") & (last_station in loader.smo["cache"])):
            loader.smo = gr.station_auto_save(loader.smo, last_station, loader.cols_list)
            #
        loader.smo, loader.cols_list = gr.station_auto_init(loader.smo, station, loader.cols_list_raw)
        last_station = station
        print("[ last station", last_station, "updated ]")
        init_state = False
        #
    json_data, df, full_station_ds = loader.get_data(station, resample="D")
    # historial_df = {}
    current_df = df
    aux_df = df
    # # # historial_df["raw"] = df
    # # historial_df["raw"] = loader.smo["raw"].copy()
    current_df.fillna(-1, inplace=True)
    print(current_df)
    print(full_station_ds)
    return json_data


@route("/data/<dataset>/<station>/<resample>")
@enable_cors
def data(dataset, station, resample):
    # global historial_df
    global full_station_ds
    global current_df
    global aux_df
    global last_station
    loader = loaders[dataset]
    station = station.upper()
    if (resample == "undefined"):
        resample = "D"
        #
    response.headers["Content-Type"] = "application/json"
    print("[ Data resample ]:", resample)
    json_data, df, full_station_ds = loader.get_data(station, resample=resample)
    return json_data


@route("/timespan/<dataset>/<station>/<resample>")
@enable_cors
def get_time_span(dataset, station, resample):
    response.headers["Content-Type"] = "application/json"
    global current_df
    timespan = 365
    timespan_status, timespan_res = verificar_ciclo_fft(current_df)
    if (timespan_status):
        timespan = timespan_res
        #
    if (resample[0] == "M"):
        timespan = timespan / 30
        #
    timespan = int(timespan)
    return { "periods": np.unique(timespan).tolist(),
             "timespan": str(timespan),
             "status": str(timespan_status) }


@route("/stats/describe/<dataset>/<station>")
@enable_cors
def get_describe(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    descriptivestats = describe_data(full_station_ds)
    # print("[ HTML ]:", descriptivestats)
    return { "describe": str(descriptivestats) }


@route("/stats/nulls/<dataset>/<station>")
@enable_cors
def get_nulls(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    reshtml = null_values_data(full_station_ds)
    # print("[ HTML ]:", reshtml)
    return { "nulls": str(reshtml) }


@route("/stats/addinfo/<dataset>/<station>")
@enable_cors
def get_addinfo(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    # reshtml = addinfo_data(full_station_ds, loader.cols_list, loader.catg_list)
    reshtml = addinfo_data(full_station_ds, loader.cols_list, [])
    # print("[ HTML ]:", reshtml)
    return { "addinfo": str(reshtml) }


@route("/stats/corrmat/<dataset>/<station>")
@enable_cors
def get_corrmat(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    reshtml = corrmat_data(full_station_ds, loader.cols_list)
    # print("[ HTML ]:", reshtml)
    return { "corrmat": str(reshtml) }


@route("/stats/bivaran/<dataset>/<station>")
@enable_cors
def get_bivaran(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    reshtml = bivaran_data(full_station_ds, loader.cols_list)
    # print("[ HTML ]:", reshtml)
    return { "bivaran": str(reshtml) }


@route("/stats/boxplot/<dataset>/<station>")
@enable_cors
def get_boxplot(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    reshtml = boxplot_data(full_station_ds, loader.cols_list)
    # print("[ HTML ]:", reshtml)
    return { "boxplot": str(reshtml) }


@route("/behavior/seasonality/<dataset>/<station>")
@enable_cors
def get_seasonality(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    reshtml = seasonality_detection(full_station_ds, loader.cols_list)
    # print("[ HTML ]:", reshtml)
    return { "seasonality": str(reshtml) }


@route("/behavior/trend/<dataset>/<station>")
@enable_cors
def get_trend(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    reshtml = trend_detection(full_station_ds, loader.cols_list)
    # print("[ HTML ]:", reshtml)
    return { "trend": str(reshtml) }


@route("/behavior/noise/<dataset>/<station>")
@enable_cors
def get_noise(dataset, station):
    response.headers["Content-Type"] = "application/json"
    global full_station_ds
    global current_df
    loader = loaders[dataset]
    reshtml = noise_detection(full_station_ds, loader.cols_list)
    # print("[ HTML ]:", reshtml)
    return { "noise": str(reshtml) }


@route("/recommendation/<dataset>/<station>")
@enable_cors
def recommendation_by_station(dataset, station):
    global last_station
    global init_state
    loader = loaders[dataset]
    # station = station[0].upper() + station[1:]
    station = station.upper()
    if init_state:
        print("[ pre-process last and current stations:", last_station, ",", station, "]")
        if ("cache" not in loader.smo):
            loader.smo["cache"] = dict()
            #
        if ((last_station != "") & (last_station in loader.smo["cache"])):
            loader.smo = gr.station_auto_save(loader.smo, last_station, loader.cols_list)
            #
        loader.smo, loader.cols_list = gr.station_auto_init(loader.smo, station, loader.cols_list_raw)
        last_station = station
        print("[ last station", last_station, "updated ]")
        init_state = False
        #
        station_metadata = loader.get_station_metadata(station)
        # -- REVERT LINE ABOVE, -TAB, OUTSIDE IF
    station_df, full_station_df = loader.get_station_df(station)
    global full_station_ds
    global current_df
    global aux_df
    global current_dataset
    global current_station
    global resultados_threads
    global dic
    global made_path
    recommendations = {
        "Data Reduction": [], # Filled with Subprocesses
        "Data Quality": [], # Filled with Subprocesses
        "Variables Behavior": [], # Filled with Subprocesses
        # # -- Excluded activities of the current subprocess
        # "Excluded Activities": [] # Filled with Subprocess Activities
    }
    dic["Excluded Activities"] = [];
    current_df = None
    # if current_df is None:
    # null_values = station_df.isna().sum().sum()
    null_values = full_station_df.isna().sum().sum()
    current_dataset = dataset
    current_station = station
    if (null_values > 0):
        dic["Clean"] = "Null Values"
        recommendations["Data Quality"].append("Clean")
        recommendations["Data Quality"].append("Nulls")
        print("[ Null Values:", null_values, "]")
    else:
        full_station_ds = full_station_df
        current_df = station_df
        aux_df = station_df
        #
    if current_df is not None:
        status_cleaning, messages_cleaning = comprobarLimpieza(current_df, par = False)
        status_norm, messages_norm = comprobarNormalizacion(current_df, par = False)
        status_transform, messages_transform = comprobarTransformacion(current_df, par = False)
        dic["Clean"] = messages_cleaning
        dic["Normalize"] = messages_norm
        dic["Transform"] = messages_transform
        if status_cleaning:
            if not gr.did_iqr_treatment(loader.smo) or not gr.did_sdv_treatment(loader.smo):
                recommendations["Data Quality"].append("Clean")
                recommendations["Data Quality"].append("Outliers")
                # gr.reset_iqr_treatment(loader.smo)
                # gr.reset_sdv_treatment(loader.smo)
                if gr.did_iqr_treatment(loader.smo):
                    dic["Excluded Activities"].append("Interquartile Range")
                    #
                if gr.did_sdv_treatment(loader.smo):
                    dic["Excluded Activities"].append("Z-Score")
                    #
        if status_norm:
            recommendations["Data Quality"].append("Normalize")
        else:
            # print("[ NOT RECOMMENDATIONS ]", not recommendations["Data Quality"])
            # print("[ NEGATIVES ]", np.any(current_df.values < 0))
            if not recommendations["Data Quality"] and np.any(current_df.values < 0):
                recommendations["Data Quality"].append("Normalize")
                dic["Excluded Activities"].append("Standard")
                dic["Excluded Activities"].append("MaxAbs")
                dic["Excluded Activities"].append("Robust")
                #
        if status_transform:
            recommendations["Data Quality"].append("Transform")
        # if not status_cleaning and not status_norm and not status_transform:
        if not status_cleaning and not status_norm:
            status_reduccion, messages_reduccion = comprobarReduccion(current_df, par = False)
            dic["DimRed"] = messages_reduccion
            messages_reduccion = []
            if status_reduccion:
                recommendations["Data Reduction"].append("DimRed")
                # print("[ DICRED: ", dic["DimRed"], "]")
                fa_treatment = [element for element in dic["DimRed"] if "FA Dim.Reduction" in element]
                if ( len(fa_treatment) == 0 ): dic["Excluded Activities"].append("Factor Analysis")
                #
            else:
                recommendations["Variables Behavior"].append("Analysis")
                #
    env = []
    res = {k: v for k, v in recommendations.items() if len(v) > 0}
    env.append(res)
    env.append(dic)
    env.append(made_path)
    dic = {}
    return json.dumps(env)


@route("/op/<dataset>/normalize/<method>")
@enable_cors
def normalize_dataset(dataset, method):
    # DEFAULT MAXABS. PENDING TO CHECK WHERE MINMAX AND STANDARD FIT
    loader = loaders[dataset]
    response.headers["Content-Type"] = "application/json"
    global current_station
    global full_station_ds
    global current_df
    global aux_df
    global made_path
    made_path.append("Normalize")
    print("[ Old df:\n", current_df, "\n]")
    if method == "minmax":
        made_path.append("MinMax")
        if gr.did_norm_w_minmax(loader.smo):
            loader.ds = loader.smo["minmax"].copy()
        else:
            # loader.ds, loader.smo = gr.norm_w_minmax(loader.smo["raw"], loader.smo, loader.cols_list)
            loader.ds, loader.smo = gr.norm_w_minmax(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "standard":
        made_path.append("Standard")
        if gr.did_norm_w_standard(loader.smo):
            loader.ds = loader.smo["standard"].copy()
        else:
            # loader.ds, loader.smo = gr.norm_w_standard(loader.smo["raw"], loader.smo, loader.cols_list)
            loader.ds, loader.smo = gr.norm_w_standard(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "maxabs":
        made_path.append("MaxAbs")
        if gr.did_norm_w_maxabs(loader.smo):
            loader.ds = loader.smo["maxabs"].copy()
        else:
            # loader.ds, loader.smo = gr.norm_w_maxabs(loader.smo["raw"], loader.smo, loader.cols_list)
            loader.ds, loader.smo = gr.norm_w_maxabs(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "robust":
        made_path.append("Robust")
        if gr.did_norm_w_robust(loader.smo):
            loader.ds = loader.smo["robust"].copy()
        else:
            # loader.ds, loader.smo = gr.norm_w_robust(loader.smo["raw"], loader.smo, loader.cols_list)
            loader.ds, loader.smo = gr.norm_w_robust(loader.smo["full"], loader.smo, loader.cols_list)
            #
    json_data, df, full_station_ds = loader.get_data(current_station, resample="D")
    current_df = df
    aux_df = df
    # # # historial_df["raw"] = df
    # # historial_df["raw"] = loader.smo["raw"].copy()
    current_df.fillna(-1, inplace=True) # DELETE
    print("[ Current df:\n", current_df, "\n]")
    return json_data


@route("/op/<dataset>/clean/<method>")
@enable_cors
def clean_dataset(dataset, method):
    loader = loaders[dataset]
    response.headers["Content-Type"] = "application/json"
    global current_station
    global full_station_ds
    global current_df
    global aux_df
    global made_path
    made_path.append("Clean")
    made_path.append("Nulls")
    if method == "rm":
        made_path.append("Rolling Mean")
        if not gr.did_fill_w_meanmedian(loader.smo):
            # loader.smo = gr.fill_w_meanmedian(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_meanmedian(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    elif method == "dtr":
        made_path.append("Decision Tree")
        if not gr.did_fill_w_decisiontree(loader.smo):
            # loader.smo = gr.fill_w_decisiontree(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_decisiontree(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    elif method == "sgb":
        made_path.append("Stochastic Gradient")
        if not gr.did_fill_w_gradientboosting(loader.smo):
            # loader.smo = gr.fill_w_gradientboosting(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_gradientboosting(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    elif method == "lwr":
        made_path.append("Locally Weighted")
        if not gr.did_fill_w_locallyweighted(loader.smo):
            # loader.smo = gr.fill_w_locallyweighted(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_locallyweighted(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    elif method == "lgd":
        made_path.append("Legendre")
        if not gr.did_fill_w_legendre(loader.smo):
            # loader.smo = gr.fill_w_legendre(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_legendre(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    elif method == "rfr":
        made_path.append("Random Forest")
        if not gr.did_fill_w_randomforest(loader.smo):
            # loader.smo = gr.fill_w_randomforest(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_randomforest(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    elif method == "knn":
        made_path.append("KNN")
        if not gr.did_fill_w_kneighbors(loader.smo):
            # loader.smo = gr.fill_w_kneighbors(loader.smo["raw"], loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            loader.smo = gr.fill_w_kneighbors(full_station_ds, loader.smo, loader.minsample, loader.valdnsize, loader.x_flr, loader.cols_list, loader.time_list)
            #
    loader.smo, loader.cols_list = gr.best_fit_to_fill(loader.smo, loader.x_flr, current_station)
    # loader.smo = gr.best_fit_to_fill(loader.smo, loader.x_flr, loader.cols_list)
    loader.ds = loader.smo["full"].copy().reset_index()
    print("[ Old df:\n", current_df, "\n]")
    json_data, df, full_station_ds = loader.get_data(current_station, resample="D")
    current_df = df
    aux_df = df
    # # historial_df["clean"] = df
    print("[ Current df:\n", current_df, "\n]")
    print("[ Null Values:", current_df.isna().sum(), "]")
    if ( current_df.isna().sum().sum() > 0 ):
        print(current_df[current_df.isna().any(axis=1)])
        #
    print("[ Full Station DS:\n", full_station_ds, "\n]")
    print("[ Null Values:", full_station_ds.isna().sum(), "]")
    return json_data


@route("/op/<dataset>/outliers/<method>")
@enable_cors
def outliers_treatment(dataset, method):
    loader = loaders[dataset]
    response.headers["Content-Type"] = "application/json"
    global current_station
    global full_station_ds
    global current_df
    global aux_df
    global made_path
    made_path.append("Clean")
    made_path.append("Outliers")
    print("[ Old df:\n", current_df, "\n]")
    if method == "iqr":
        made_path.append("Interquartile Range")
        if gr.did_iqr_treatment(loader.smo):
            loader.ds = loader.smo["iqr"].copy()
        else:
            loader.ds, loader.smo = gr.iqr_treatment(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "sdv":
        made_path.append("Z-Score")
        if gr.did_sdv_treatment(loader.smo):
            loader.ds = loader.smo["sdv"].copy()
        else:
            loader.ds, loader.smo = gr.sdv_treatment(loader.smo["full"], loader.smo, loader.cols_list)
            #
    json_data, df, full_station_ds = loader.get_data(current_station, resample="D")
    current_df = df
    aux_df = df
    # # # historial_df["raw"] = df
    # # historial_df["raw"] = loader.smo["raw"].copy()
    # current_df.fillna(-1, inplace=True) # DELETE
    print("[ Current df:\n", current_df, "\n]")
    return json_data


@route("/op/<dataset>/transform/<method>/<number>")
@enable_cors
def transform_dataset(dataset, method, number):
    loader = loaders[dataset]
    response.headers["Content-Type"] = "application/json"
    global current_station
    global full_station_ds
    global current_df
    global aux_df
    global made_path
    made_path.append("Transform")
    print("[ Old df:\n", current_df, "\n]")
    if method == "linear":
        made_path.append("Linear")
        if gr.did_linear_transform(loader.smo):
            loader.ds = loader.smo["linear"].copy()
        else:
            loader.ds, loader.smo = gr.linear_transform(number, loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "quadratic":
        made_path.append("Quadratic")
        if gr.did_quadratic_transform(loader.smo):
            loader.ds = loader.smo["quadratic"].copy()
        else:
            loader.ds, loader.smo = gr.quadratic_transform(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "log":
        made_path.append("Logarithm")
        if gr.did_log_transform(loader.smo):
            loader.ds = loader.smo["log"].copy()
        else:
            loader.ds, loader.smo = gr.log_transform(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "sqrt":
        made_path.append("Square Root")
        if gr.did_sqrt_transform(loader.smo):
            loader.ds = loader.smo["sqrt"].copy()
        else:
            loader.ds, loader.smo = gr.sqrt_transform(loader.smo["full"], loader.smo, loader.cols_list)
            #
    elif method == "diff":
        made_path.append("Differencing")
        if gr.did_diff_transform(loader.smo):
            loader.ds = loader.smo["diff"].copy()
        else:
            loader.ds, loader.smo = gr.diff_transform(loader.smo["full"], loader.smo, loader.cols_list)
            #
    json_data, df, full_station_ds = loader.get_data(current_station, resample="D")
    current_df = df
    aux_df = df
    # # # historial_df["raw"] = df
    # # historial_df["raw"] = loader.smo["raw"].copy()
    current_df.fillna(-1, inplace=True) # DELETE
    print("[ Current df:\n", current_df, "\n]")
    return json_data


@route("/op/<dataset>/reduce/<method>/<n_comp>")
@enable_cors
def reduce_dataset(dataset, method, n_comp):
    loader = loaders[dataset]
    response.headers["Content-Type"] = "application/json"
    global current_station
    global full_station_ds
    global current_df
    global aux_df
    global made_path
    made_path.append("DimRed")
    res = True
    if method == "factor":
        made_path.append("Factor Analysis")
        # status_reduccion, messages_reduccion = comprobarReduccion(current_df, par = False)
        res, n_comp = check_dimensionality_reduction_fa(current_df)
        #
    elif method == "manual":
        made_path.append("PCA and correlation")
        n_comp = re.sub(", +", ",", n_comp).split(",")
        #
    if res:
        loader.smo, loader.cols_list = gr.drop_features(loader.smo, loader.cols_list, n_comp)
        loader.ds = loader.smo["full"].copy().reset_index()
        #
    print("[ Old df:\n", current_df, "\n]")
    json_data, df, full_station_ds = loader.get_data(current_station, resample="D")
    current_df = df
    aux_df = df
    print("[ Current df:\n", current_df, "\n]")
    return json_data


@route("/op/<dataset>/vbehavior/<operator>")
@enable_cors
def vbehavior_analyse(dataset, operator):
    response.headers["Content-Type"] = "application/json"

    global current_df

    data = current_df.values

    data[data < 0] = -1

    if request.query:
        feature = int(request.query.feature)

    dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(current_df.index))

    resample = "W"

    # If it is not precipitation then use the mean to resample
    if feature > 0:
        res_dataframe = dataframe.resample(resample).mean()[feature]

    # Else use the maximum value to resample
    else:
        res_dataframe = dataframe.resample(resample).max()[feature]

    # operator seasonal_decompose
    if operator in ["trend", "seasonality"]:
        decomposition = sm.tsa.seasonal_decompose(
            res_dataframe, model="aditive")
        if operator == "trend":
            feature_data = decomposition.trend.values
        elif operator == "seasonality":
            feature_data = decomposition.seasonal.values
        else:
            feature_data = []

    # Fourier
    elif operator == "cyclicity":
        y = res_dataframe.values
        fourier_output = np.abs(fft.fft(y))
        frecuencies = fft.fftfreq(len(y))
        peaks = sig.find_peaks(fourier_output, prominence=10**2)[0]

        print(peaks)
        peak_freq = frecuencies[peaks]
        peak_power = fourier_output[peaks]

        output = pd.DataFrame()

        output["index"] = peaks
        output["freq (1/hour)"] = peak_freq
        output["amplitude"] = peak_power
        output["period (days)"] = 1/peak_freq
        output["fft"] = fourier_output[peaks]
        output = output.sort_values("amplitude", ascending=False)

        print(output)

        max_amp_index = output["index"].iloc[0:5:2]

        filtered_fft_output = np.array(
            [f if i in max_amp_index.values else 0 for i, f in enumerate(fourier_output)])

        filtered_sig = fft.ifft(filtered_fft_output)
        print("output shape:", filtered_fft_output.shape,
              fourier_output.shape, y.shape)
        feature_data = np.array(filtered_sig.astype("float"))

    feature_data = np.array([feature_data]).T
    feature_data = np.append(feature_data, np.array(
        [res_dataframe.values]).T, axis=1)
    # print(feature_data.shape, res_dataframe.values.shape, feature_data)

    current_df = dataframe
    return dataframe.reset_index().to_json(orient="records", index=True)


@route("/op/<dataset>/raw")
@enable_cors
def raw_dataset(dataset):
    global current_dataset
    global current_station
    global full_station_ds
    global current_df
    loader = loaders[current_dataset]
    response.headers["Content-Type"] = "application/json"
    json_data, df, full_station_ds = loader.get_raw_data(current_station, resample="D")
    current_df = df
    current_df.fillna(-1, inplace=True) # DELETE
    print(current_df)
    return json_data


@route("/src/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="./src")


# Set reloader=False when the development finishes to accel the program.
bottle.run(host="localhost", reloader=True, debug=True)
