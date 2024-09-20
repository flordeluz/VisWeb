# -*- mode: python -*-
#
# Copyright (C) 2024  Victor C. Salas P.
#
# Author: Victor C. Salas P. <nmagko@gmail.com>

from .Mainredo import MainredoClass
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import re
import json
# from IPython.display import display
# Rolling Mean & Moving Median
from statistics import mean, median, mode
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score, mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler, RobustScaler
# Decision Trees
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
# Stochastic Gradient Boosting
from sklearn.ensemble import GradientBoostingRegressor
# Locally Weighted Regression
from statsmodels.api import nonparametric
from scipy.interpolate import make_interp_spline
from scipy.interpolate import make_lsq_spline
from scipy.interpolate import CubicSpline
from scipy.interpolate import make_smoothing_spline
lowess = nonparametric.lowess
# Legendre Polynomials
from scipy.special import eval_legendre
# Random Forest
from sklearn.ensemble import RandomForestRegressor
# KNeighbors
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import BaggingRegressor

# PRIVATE FUNCTIONS

def wmape(y_true, y_pred):
    return np.abs(y_true - y_pred).sum() / np.abs(y_true).sum()


def metricf(y_val, o):
    y_a = y_val.copy()
    y_h = o.y_val.copy()
    y_a = y_a.values.reshape(-1, 1) if isinstance(y_a, pd.Series) else y_a.reshape(-1, 1)
    y_h = y_h.values.reshape(-1, 1) if isinstance(y_h, pd.Series) else y_h.reshape(-1, 1)
    s = MaxAbsScaler()
    s.fit(y_a)
    y_a = s.transform(y_a)
    y_h = s.transform(y_h)
    o.mae = mean_absolute_error(y_a, y_h)
    o.mse = mean_squared_error(y_a, y_h)
    o.rmse = np.sqrt(mean_squared_error(y_a, y_h))
    o.medae = median_absolute_error(y_a, y_h)
    o.r2 = r2_score(y_a, y_h)
    o.mape = mean_absolute_percentage_error(y_a, y_h)
    o.wmape = wmape(y_a, y_h)


def metricvf(o):
    return [o.label, o.mae, o.mse, o.rmse, o.medae, o.r2, o.mape, o.wmape]


def metricdff(columns = ["MODEL", "MAE", "MSE", "RMSE", "MEDAE", "R2", "MAPE", "WMAPE"]):
    return pd.DataFrame(columns = columns)


def metricarf(f, v): f.loc[len(f)] = v


def metricamaper2f(X, y, *o):
    tmp_o = lambda: None
    for dsta_o in o:
        # Verificar wmape y r2
        if not hasattr(tmp_o, "label"):
            tmp_o = dsta_o
        else:
            if (tmp_o.wmape > dsta_o.wmape):
                tmp_o = lambda: None
                tmp_o = dsta_o
                #
    tmp_o.X_src = X.copy()
    tmp_o.y_src = y.copy()
    return tmp_o


# def highlight_rmse(rmse, color):
#     if ((rmse.to_numpy()>0) & (rmse.to_numpy()<=0.5)).any():
#         return np.where((rmse == np.nanmin(rmse[np.where(np.logical_and(rmse.to_numpy()>0, rmse.to_numpy()<=0.5))[0]].to_numpy())), f"background: {color};", None)
#     else:
#         return (np.nan, )


# def highlight_r2(r2, color):
#     if ((r2.to_numpy()>0.6) & (r2.to_numpy()<=1)).any():
#         return np.where((r2 == np.nanmax(r2[np.where(np.logical_and(r2.to_numpy()>0.6, r2.to_numpy()<=1))[0]].to_numpy())), f"background: {color};", None)
#     else:
#         return (np.nan, )


def nfindsf(h, o, prognl):
    for k, v in o.items(): # PROG
        if k in prognl: # JUST VALID PROG ENTRIES
            for l, v in o[k].items(): # ESTACION
                for m, v in o[k][l].items(): # FEATURE
                    if hasattr(o[k][l][m], "label"):
                        metricarf(h, [k, l, m] + metricvf(o[k][l][m]))
                    # else:
                    #     print("Warning:", [k, l, m] + ["EMPTY", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN], "excluded.")
                        #
    return h

# CLASS DEFINITION

class GenRedo(MainredoClass):
    def __init__(self):
        super().__init__()
        print("[ Transformations Handler ]")
        self.name = "redo"
        self.prognl = ["RM", "DTR", "SGB", "LWR", "LGD", "RFR", "KNN"]
        self.methal = {
            "outliers": ["iqr", "sdv"],
            "transform": ["linear", "quadratic", "log", "sqrt", "diff"],
            "norm": ["maxabs", "minmax", "standard", "robust"],
            "fill": ["meanmedian", "decisiontree", "gradientboosting", "locallyweighted", "legendre", "randomforest", "kneighbors"]
        }
        print("[ Enabled programs:", self.prognl, "]")
        print("[ Enabled methods algorithms:", json.dumps(self.methal, indent=4), "]")
        
        
    def iqr_treatment(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "outliers"
        algorm = "iqr"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            for feature in cols_list:
                serie = smo[algorm][feature]
                q1 = np.percentile(serie, 25)
                q3 = np.percentile(serie, 75)
                iqr = q3 - q1
                # Calcular los límites de los valores atípicos
                lim_inf = q1 - 1.5 * iqr
                lim_sup = q3 + 1.5 * iqr
                serie[(serie < lim_inf) | (serie > lim_sup)] = np.nan
                #
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            # COPY TO FULL - COMMENT IF FAILS
            smo["full"] = smo[algorm].copy()
            print(smo["full"].info())
            print(smo["full"]["station"].unique())
            # END COPY TO FULL
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo
    
    
    def did_iqr_treatment(self, smo):
        # Private constants by method and algo
        method = "outliers"
        algorm = "iqr"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True
        
        
    def sdv_treatment(self, ds, smo, cols_list, z_threshold = 2):
        # Private constants by method and algo
        method = "outliers"
        algorm = "sdv"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            for feature in cols_list:
                serie = smo[algorm][feature]
                mean = np.mean(serie)
                sd = np.std(serie)
                # Calcular el Z-score
                z_scores = np.abs((serie - mean) / sd)
                serie[z_scores > z_threshold] = np.nan
                #
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            # COPY TO FULL - COMMENT IF FAILS
            smo["full"] = smo[algorm].copy()
            print(smo["full"].info())
            print(smo["full"]["station"].unique())
            # END COPY TO FULL
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo
    
    
    def did_sdv_treatment(self, smo):
        # Private constants by method and algo
        method = "outliers"
        algorm = "sdv"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True
        
        
    def linear_transform(self, num, ds, smo, cols_list):
        # Private constants by method and algo
        method = "transform"
        algorm = "linear"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            num = int(num)
            smo[algorm] = ds.copy()
            smo[algorm][cols_list] = smo[algorm][cols_list].apply(lambda x: x.astype("float64") * num, axis=0)
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo
    
    
    def did_linear_transform(self, smo):
        # Private constants by method and algo
        method = "transform"
        algorm = "linear"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True
        
        
    def quadratic_transform(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "transform"
        algorm = "quadratic"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            smo[algorm][cols_list] = smo[algorm][cols_list].apply(lambda x: x.astype("float64") ** 2, axis=0)
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_quadratic_transform(self, smo):
        # Private constants by method and algo
        method = "transform"
        algorm = "quadratic"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def log_transform(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "transform"
        algorm = "log"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            smo[algorm][cols_list] = smo[algorm][cols_list].apply(lambda x: np.log(x.astype("float64")), axis=0)
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_log_transform(self, smo):
        # Private constants by method and algo
        method = "transform"
        algorm = "log"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def sqrt_transform(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "transform"
        algorm = "sqrt"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            smo[algorm][cols_list] = smo[algorm][cols_list].apply(lambda x: np.sqrt(x.astype("float64")), axis=0)
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_sqrt_transform(self, smo):
        # Private constants by method and algo
        method = "transform"
        algorm = "sqrt"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def diff_transform(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "transform"
        algorm = "diff"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            # smo[algorm][cols_list] = smo[algorm][cols_list].apply(lambda x: np.diff(x.astype("float64")), axis=0)
            smo[algorm][cols_list] = smo[algorm][cols_list] - smo[algorm][cols_list].shift(periods = 1)
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_diff_transform(self, smo):
        # Private constants by method and algo
        method = "transform"
        algorm = "diff"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def norm_w_maxabs(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "norm"
        algorm = "maxabs"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            sc = MaxAbsScaler()
            smo[algorm][cols_list] = sc.fit_transform(smo[algorm][cols_list])
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_norm_w_maxabs(self, smo):
        # Private constants by method and algo
        method = "norm"
        algorm = "maxabs"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def norm_w_minmax(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "norm"
        algorm = "minmax"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            sc = MinMaxScaler()
            smo[algorm][cols_list] = sc.fit_transform(smo[algorm][cols_list])
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_norm_w_minmax(self, smo):
        # Private constants by method and algo
        method = "norm"
        algorm = "minmax"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def norm_w_standard(self, ds, smo, cols_list): # ZScoreScaler = StandardScaler
        # Private constants by method and algo
        method = "norm"
        algorm = "standard"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            sc = StandardScaler()
            smo[algorm][cols_list] = sc.fit_transform(smo[algorm][cols_list])
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_norm_w_standard(self, smo):
        # Private constants by method and algo
        method = "norm"
        algorm = "standard"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def norm_w_robust(self, ds, smo, cols_list):
        # Private constants by method and algo
        method = "norm"
        algorm = "robust"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            smo[algorm] = ds.copy()
            sc = RobustScaler()
            smo[algorm][cols_list] = sc.fit_transform(smo[algorm][cols_list])
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo[algorm].copy().reset_index(), smo


    def did_norm_w_robust(self, smo):
        # Private constants by method and algo
        method = "norm"
        algorm = "robust"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_meanmedian(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "meanmedian"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # Rolling mean and Moving median
            progn = "RM"
            smo[progn] = dict() # smo[PROG]
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                dsta = ds[ds[x_flr] == n_fld].copy()
                dstr = ds[ds[x_flr] == n_fld].copy()
                dstm = ds[ds[x_flr] == n_fld].copy()
                for y_fld in cols_list:
                    nulls_wnd = (dsta[y_fld]).isnull().sum() + 1
                    nonulls_wnd = len(dsta[y_fld]) - nulls_wnd + 2
                    # First pass: Nulls count is the window size for mean and median, Not nulls count is the windows size for mode
                    dsta[y_fld + "_rm"] = (dsta[y_fld]).rolling(window=nulls_wnd, min_periods=1).mean()
                    dsta[y_fld + "_mm"] = (dsta[y_fld]).rolling(window=nulls_wnd, min_periods=1).median()
                    # Second pass: Softing window size of 7
                    dstr.loc[dstr[y_fld].isnull(), y_fld] = dsta[y_fld + "_rm"][dstr[y_fld].isnull()]
                    dsta[y_fld + "_rm"] = (dstr[y_fld]).rolling(window=7, min_periods=1).mean()
                    dstm.loc[dstm[y_fld].isnull(), y_fld] = dsta[y_fld + "_mm"][dstm[y_fld].isnull()]
                    dsta[y_fld + "_mm"] = (dstm[y_fld]).rolling(window=7, min_periods=1).median()
                    #
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta_nu = dsta.copy()
                    dsta_nu = dsta_nu[dsta_nu[y_dep].isnull()]
                    dsta_nn = lambda: None
                    setattr(dsta_nn, y_dep, dsta.copy())
                    setattr(dsta_nn, y_dep, getattr(dsta_nn, y_dep).dropna(subset=[y_dep]))
                    if (dsta.shape[0] > dsta[y_dep].isnull().sum() and 
                        dsta.shape[0] > dsta[y_dep + "_rm"].isnull().sum() and
                        dsta.shape[0] > dsta[y_dep + "_mm"].isnull().sum() and getattr(dsta_nn, y_dep).shape[0] >= minsample):
                        # Hint: setattr(x, 'foobar', 123) is the same as x.foobar = 123
                        # Hint: getattr(x, 'foobar') is the same as x.foobar
                        metdf = metricdff()
                        for x_fld in time_list:
                            X_tra, X_val, y_tra, y_val = train_test_split(getattr(dsta_nn, y_dep)[x_fld], getattr(dsta_nn, y_dep)[y_dep], test_size=valdnsize, shuffle = False, stratify = None)
                            X_tra_rm, X_val_rm, y_tra_rm, y_val_rm = train_test_split(getattr(dsta_nn, y_dep)[x_fld], getattr(dsta_nn, y_dep)[y_dep + "_rm"], test_size=valdnsize, shuffle = False, stratify = None)
                            X_tra_mm, X_val_mm, y_tra_mm, y_val_mm = train_test_split(getattr(dsta_nn, y_dep)[x_fld], getattr(dsta_nn, y_dep)[y_dep + "_mm"], test_size=valdnsize, shuffle = False, stratify = None)
                            dsta_rm = lambda: None
                            dsta_rm.y_val = y_val_rm.copy()
                            dsta_rm.label = y_dep + "_rm"
                            dsta_rm.X_tgt = dsta_nu[x_fld].copy()
                            dsta_rm.y_hat = dsta_nu[dsta_rm.label].copy()
                            metricf(y_val, dsta_rm)
                            metricarf(metdf, metricvf(dsta_rm))
                            dsta_mm = lambda: None
                            dsta_mm.y_val = y_val_mm.copy()
                            dsta_mm.label = y_dep + "_mm"
                            dsta_mm.X_tgt = dsta_nu[x_fld].copy()
                            dsta_mm.y_hat = dsta_nu[dsta_mm.label].copy()
                            metricf(y_val, dsta_mm)
                            metricarf(metdf, metricvf(dsta_mm))
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], dsta_rm, dsta_mm)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DEL MODELO DE MEDIA Y MEDIANA MOVIL")
                    #     print("=" * 68)
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta[y_dep].isnull().sum())
                    #     print("||", y_dep + "_rm", "VALORES NULOS EN MEDIA MÓVIL:", dsta[y_dep + "_rm"].isnull().sum())
                    #     print("||", y_dep + "_mm", "VALORES NULOS EN MEDIANA MÓVIL:", dsta[y_dep + "_mm"].isnull().sum())
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
                        
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_meanmedian(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "meanmedian"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_decisiontree(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "decisiontree"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # Decision Trees
            progn = "DTR"
            smo[progn] = dict() # smo[PROG]
            hparams = {
                "max_depth": [None, 5, 10],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4]
            }
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta = ds[ds[x_flr] == n_fld].copy()
                    dsta_nonulls = dsta.copy()
                    dsta_nonulls = dsta_nonulls.dropna(subset=[y_dep])
                    dsta_nulls = dsta.copy()
                    dsta_nulls = dsta_nulls[dsta_nulls[y_dep].isnull()]
                    if (dsta_nonulls.shape[0] + dsta_nulls.shape[0] > dsta_nulls.shape[0] and dsta_nonulls.shape[0] >= minsample):
                        for x_fld in time_list:
                            X_tr = dsta_nonulls[x_fld]
                            y_tr = dsta_nonulls[y_dep]
                            X_tra, X_val, y_tra, y_val = train_test_split(X_tr.values.reshape(-1, 1), y_tr, test_size=valdnsize, random_state=13)
                            metdf = metricdff()
                            regr_1 = lambda: None
                            regr_1 = DecisionTreeRegressor()
                            regr_1.label = "Tree"
                            regr_1.fit(X_tra, y_tra)
                            regr_1.y_val = regr_1.predict(X_val)
                            metricf(y_val, regr_1)
                            metricarf(metdf, metricvf(regr_1))
                            regr_2 = lambda: None
                            regr_2 = GridSearchCV(DecisionTreeRegressor(), hparams)
                            regr_2.label = "Tuned Tree"
                            regr_2.fit(X_tra, y_tra)
                            regr_2.y_val = regr_2.predict(X_val)
                            metricf(y_val, regr_2)
                            metricarf(metdf, metricvf(regr_2))
                            X_ts = dsta_nulls[x_fld]
                            y_t1 = regr_1.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_1.X_tgt = X_ts.copy()
                            regr_1.y_hat = pd.Series(y_t1, index=regr_1.X_tgt.index).copy() if (len(y_t1) > 0) else pd.Series().copy()
                            y_t2 = regr_2.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_2.X_tgt = X_ts.copy()
                            regr_2.y_hat = pd.Series(y_t2, index=regr_2.X_tgt.index).copy() if (len(y_t2) > 0) else pd.Series().copy()
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], regr_1, regr_2)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DE REGRESIÓN DEL ÁRBOL DE DECISIÓN")
                    #     print("=" * 68)
                    #     print("||", y_dep, "VALORES EN TOTAL:", dsta_nonulls.shape[0] + dsta_nulls.shape[0])
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta_nulls.shape[0])
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_decisiontree(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "decisiontree"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_gradientboosting(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "gradientboosting"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # Stochastic Gradient Boosting
            progn = "SGB"
            smo[progn] = dict() # smo[PROG]
            dparams = dict(
                learning_rate=0.05,
                n_estimators=200,
                max_depth=2,
                min_samples_leaf=9,
                min_samples_split=9,
            )
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta = ds[ds[x_flr] == n_fld].copy()
                    dsta_nonulls = dsta.copy()
                    dsta_nonulls = dsta_nonulls.dropna(subset=[y_dep])
                    dsta_nulls = dsta.copy()
                    dsta_nulls = dsta_nulls[dsta_nulls[y_dep].isnull()]
                    if (dsta_nonulls.shape[0] + dsta_nulls.shape[0] > dsta_nulls.shape[0] and dsta_nonulls.shape[0] >= minsample):
                        for x_fld in time_list:
                            X_tr = dsta_nonulls[x_fld]
                            y_tr = dsta_nonulls[y_dep]
                            X_tra, X_val, y_tra, y_val = train_test_split(X_tr.values.reshape(-1, 1), y_tr, test_size=valdnsize, random_state=13)
                            metdf = metricdff()
                            regr_1 = lambda: None
                            regr_1 = GradientBoostingRegressor(random_state=0)
                            regr_1.label = "SGB"
                            regr_1.fit(X_tra, y_tra)
                            regr_1.y_val = regr_1.predict(X_val)
                            metricf(y_val, regr_1)
                            metricarf(metdf, metricvf(regr_1))
                            regr_2 = lambda: None
                            regr_2 = GradientBoostingRegressor(loss="quantile", alpha=0.05, **dparams) # alpha = [0.05, 0.5, 0.95]
                            regr_2.label = "SGB Quantile"
                            regr_2.fit(X_tra, y_tra)
                            regr_2.y_val = regr_2.predict(X_val)
                            metricf(y_val, regr_2)
                            metricarf(metdf, metricvf(regr_2))
                            regr_3 = lambda: None
                            regr_3 = GradientBoostingRegressor(loss="squared_error", **dparams)
                            regr_3.label = "SGB Squared"
                            regr_3.fit(X_tra, y_tra)
                            regr_3.y_val = regr_3.predict(X_val)
                            metricf(y_val, regr_3)
                            metricarf(metdf, metricvf(regr_3))
                            X_ts = dsta_nulls[x_fld]
                            y_t1 = regr_1.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_1.X_tgt = X_ts.copy()
                            regr_1.y_hat = pd.Series(y_t1, index=regr_1.X_tgt.index).copy() if (len(y_t1) > 0) else pd.Series().copy()
                            y_t2 = regr_2.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_2.X_tgt = X_ts.copy()
                            regr_2.y_hat = pd.Series(y_t2, index=regr_2.X_tgt.index).copy() if (len(y_t2) > 0) else pd.Series().copy()
                            y_t3 = regr_3.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_3.X_tgt = X_ts.copy()
                            regr_3.y_hat = pd.Series(y_t3, index=regr_3.X_tgt.index).copy() if (len(y_t3) > 0) else pd.Series().copy()
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], regr_1, regr_2, regr_3)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DE REGRESIÓN ADITIVA (SGB)")
                    #     print("=" * 68)
                    #     print("||", y_dep, "VALORES EN TOTAL:", dsta_nonulls.shape[0] + dsta_nulls.shape[0])
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta_nulls.shape[0])
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
            
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_gradientboosting(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "gradientboosting"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_locallyweighted(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "locallyweighted"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # Locally Weighted Regression
            progn = "LWR"
            smo[progn] = dict() # smo[PROG]
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta = ds[ds[x_flr] == n_fld].copy()
                    dsta_nonulls = dsta.copy()
                    dsta_nonulls = dsta_nonulls.dropna(subset=[y_dep])
                    dsta_nulls = dsta.copy()
                    dsta_nulls = dsta_nulls[dsta_nulls[y_dep].isnull()]
                    if (dsta_nonulls.shape[0] + dsta_nulls.shape[0] > dsta_nulls.shape[0] and dsta_nonulls.shape[0] >= minsample):
                        for x_fld in time_list:
                            X_tr = dsta_nonulls[x_fld].to_numpy(dtype="datetime64").astype(np.timedelta64) / np.timedelta64(1, "s")
                            y_tr = dsta_nonulls[y_dep].to_numpy()
                            X_tra, X_val, y_tra, y_val = train_test_split(X_tr, y_tr, test_size=valdnsize, shuffle = False, stratify = None)
                            delta = 0.01*(max(X_tra)-min(X_tra)) if (max(X_tra)-min(X_tra)) > 5000 else 0.0
                            metdf = metricdff()
                            regr_1 = lambda: None
                            regr_1.k = 1
                            regr_1.y = lowess(y_tra, X_tra, frac=1/10, delta=delta, return_sorted=False)
                            regr_1.predict = np.interp
                            regr_1.label = "LWR Linear"
                            regr_1.y_val = regr_1.predict(X_val, X_tra, regr_1.y)
                            metricf(y_val, regr_1)
                            metricarf(metdf, metricvf(regr_1))
                            regr_2 = lambda: None
                            regr_2.k = 3
                            regr_2.y = lowess(y_tra, X_tra, frac=1/7, delta=delta, return_sorted=False)
                            regr_2.t = np.r_[(X_tra[0],)*(regr_2.k+1), (X_tra[int(X_tra.size/2)],)*regr_2.k, (X_tra[-1],)*(regr_2.k+1)]
                            regr_2.predict = make_lsq_spline(X_tra, regr_2.y, regr_2.t, k=regr_2.k)
                            regr_2.label = "LWR Least SQuared"
                            regr_2.y_val = regr_2.predict(X_val)
                            metricf(y_val, regr_2)
                            metricarf(metdf, metricvf(regr_2))
                            X_ts = dsta_nulls[x_fld].to_numpy(dtype="datetime64").astype(np.timedelta64) / np.timedelta64(1, "s")
                            y_t1 = regr_1.predict(X_ts, X_tra, regr_1.y) if (len(X_ts) > 0) else X_ts
                            regr_1.y_hat = pd.Series(y_t1, index=dsta_nulls[x_fld].index).copy() if (len(y_t1) > 0) else pd.Series().copy()
                            y_t2 = regr_2.predict(X_ts) if (len(X_ts) > 0) else X_ts
                            regr_2.y_hat = pd.Series(y_t2, index=dsta_nulls[x_fld].index).copy() if (len(y_t2) > 0) else pd.Series().copy()
                            X_tr = pd.to_datetime(X_tr, unit="s")
                            X_ts = pd.to_datetime(X_ts, unit="s")
                            regr_1.X_tgt = pd.Series(X_ts, index=dsta_nulls[x_fld].index).copy() if (len(X_ts) > 0) else pd.Series().copy()
                            regr_2.X_tgt = pd.Series(X_ts, index=dsta_nulls[x_fld].index).copy() if (len(X_ts) > 0) else pd.Series().copy()
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], regr_1, regr_2)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DE REGRESIÓN PONDERADA LOCALMENTE (LWR)")
                    #     print("=" * 68)
                    #     print("||", y_dep, "VALORES EN TOTAL:", dsta_nonulls.shape[0] + dsta_nulls.shape[0])
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta_nulls.shape[0])
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
                
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_locallyweighted(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "locallyweighted"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_legendre(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "legendre"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # Legendre Polynomials
            progn = "LGD"
            smo[progn] = dict() # smo[PROG]
            dv10 = 10**10
            degree = 5
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta = ds[ds[x_flr] == n_fld].copy()
                    dsta_nonulls = dsta.copy()
                    dsta_nonulls = dsta_nonulls.dropna(subset=[y_dep])
                    dsta_nulls = dsta.copy()
                    dsta_nulls = dsta_nulls[dsta_nulls[y_dep].isnull()]
                    if (dsta_nonulls.shape[0] + dsta_nulls.shape[0] > dsta_nulls.shape[0] and dsta_nonulls.shape[0] >= minsample):
                        for x_fld in time_list:
                            X_tr = dsta_nonulls[x_fld].to_numpy(dtype="datetime64").astype(np.timedelta64) / np.timedelta64(1, "s") / dv10
                            y_tr = dsta_nonulls[y_dep].to_numpy()
                            X_tra, X_val, y_tra, y_val = train_test_split(X_tr, y_tr, test_size=valdnsize, shuffle = False, stratify = None)
                            X_ts = dsta_nulls[x_fld].to_numpy(dtype="datetime64").astype(np.timedelta64) / np.timedelta64(1, "s") / dv10
                            metdf = metricdff()
                            regr_1 = lambda: None
                            regr_1.X = np.column_stack([eval_legendre(w, X_tra) for w in range(degree)])
                            regr_1.theta = np.linalg.lstsq(regr_1.X, y_tra, rcond=None)[0]
                            regr_1.label = "Legendre"
                            regr_1.y_val = np.zeros(X_val.size)
                            for w in range(degree): regr_1.y_val += regr_1.theta[w]*eval_legendre(w, X_val)
                            metricf(y_val, regr_1)
                            metricarf(metdf, metricvf(regr_1))
                            if (len(X_ts) > 0):
                                regr_1.y_hat = np.zeros(X_ts.size)
                                for w in range(degree): regr_1.y_hat += regr_1.theta[w]*eval_legendre(w, X_ts)
                            else:
                                regr_1.y_hat = X_ts
                                #
                            regr_1.y_hat = pd.Series(regr_1.y_hat, index=dsta_nulls[x_fld].index).copy() if (len(regr_1.y_hat) > 0) else pd.Series().copy()
                            X_tr = pd.to_datetime(X_tr * dv10, unit="s")
                            X_ts = pd.to_datetime(X_ts * dv10, unit="s")
                            regr_1.X_tgt = pd.Series(X_ts, index=dsta_nulls[x_fld].index).copy() if (len(X_ts) > 0) else pd.Series().copy()
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], regr_1)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DE REGRESIÓN CON POLINOMIOS DE LEGENDRE")
                    #     print("=" * 68)
                    #     print("||", y_dep, "VALORES EN TOTAL:", dsta_nonulls.shape[0] + dsta_nulls.shape[0])
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta_nulls.shape[0])
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
                
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_legendre(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "legendre"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_randomforest(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "randomforest"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # Random Forest
            progn = "RFR"
            smo[progn] = dict() # smo[PROG]
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta = ds[ds[x_flr] == n_fld].copy()
                    dsta_nonulls = dsta.copy()
                    dsta_nonulls = dsta_nonulls.dropna(subset=[y_dep])
                    dsta_nulls = dsta.copy()
                    dsta_nulls = dsta_nulls[dsta_nulls[y_dep].isnull()]
                    if (dsta_nonulls.shape[0] + dsta_nulls.shape[0] > dsta_nulls.shape[0] and dsta_nonulls.shape[0] >= minsample):
                        for x_fld in time_list:
                            X_tr = dsta_nonulls[x_fld]
                            y_tr = dsta_nonulls[y_dep]
                            X_tra, X_val, y_tra, y_val = train_test_split(X_tr.values.reshape(-1, 1), y_tr, test_size=valdnsize, random_state=13)
                            metdf = metricdff()
                            regr_1 = lambda: None
                            regr_1 = RandomForestRegressor(max_depth=int(np.log2(len(X_tra))), oob_score=True, n_jobs=-1, random_state=13)
                            regr_1.label = "Random Forest"
                            regr_1.fit(X_tra, y_tra)
                            regr_1.y_val = regr_1.predict(X_val)
                            metricf(y_val, regr_1)
                            metricarf(metdf, metricvf(regr_1))
                            X_ts = dsta_nulls[x_fld]
                            y_t1 = regr_1.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_1.X_tgt = X_ts.copy()
                            regr_1.y_hat = pd.Series(y_t1, index=regr_1.X_tgt.index).copy() if (len(y_t1) > 0) else pd.Series().copy()
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], regr_1)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DE REGRESIÓN RANDOM FOREST")
                    #     print("=" * 68)
                    #     print("||", y_dep, "VALORES EN TOTAL:", dsta_nonulls.shape[0] + dsta_nulls.shape[0])
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta_nulls.shape[0])
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
                
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_randomforest(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "randomforest"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def fill_w_kneighbors(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list):
        # Private constants by method and algo
        method = "fill"
        algorm = "kneighbors"
        # Structure init. It has to be done in each algo method.
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    smo[self.name][method][algorm] = False
            else:
                smo[self.name][method] = dict()
                smo[self.name][method][algorm] = False
        else:
            smo[self.name] = dict()
            smo[self.name][method] = dict()
            smo[self.name][method][algorm] = False
            # Algo's body
        if not smo[self.name][method][algorm]:
            # Algo's code goes here
            # -------------------------------
            
            # K Nearest Neighbors
            progn = "KNN"
            smo[progn] = dict() # smo[PROG]
            hparams = {
                "n_neighbors": [1, 2, 3, 5, 7, 11, 13, 17, 19, 23],
                "weights": ["uniform", "distance"],
            }
            for n_fld in ds[x_flr].unique():
                smo[progn][n_fld] = dict() # smo[PROG][ESTACION]
                for y_dep in cols_list:
                    #*# FOR FEATURES ->
                    smo[progn][n_fld][y_dep] = dict() # smo[PROG][ESTACION][FEATURE]
                    dsta = ds[ds[x_flr] == n_fld].copy()
                    dsta_nonulls = dsta.copy()
                    dsta_nonulls = dsta_nonulls.dropna(subset=[y_dep])
                    dsta_nulls = dsta.copy()
                    dsta_nulls = dsta_nulls[dsta_nulls[y_dep].isnull()]
                    if (dsta_nonulls.shape[0] + dsta_nulls.shape[0] > dsta_nulls.shape[0] and dsta_nonulls.shape[0] >= minsample):
                        for x_fld in time_list:
                            X_tr = dsta_nonulls[x_fld]
                            y_tr = dsta_nonulls[y_dep]
                            X_tra, X_val, y_tra, y_val = train_test_split(X_tr.values.reshape(-1, 1), y_tr, test_size=valdnsize, random_state=13)
                            metdf = metricdff()
                            regr_1 = lambda: None
                            regr_1 = GridSearchCV(KNeighborsRegressor(), hparams)
                            regr_1.label = "kNN"
                            regr_1.fit(X_tra, y_tra)
                            regr_1.y_val = regr_1.predict(X_val)
                            metricf(y_val, regr_1)
                            metricarf(metdf, metricvf(regr_1))
                            regr_2 = lambda: None
                            regr_2_bknn = KNeighborsRegressor(n_neighbors=regr_1.best_params_["n_neighbors"], weights=regr_1.best_params_["weights"])
                            regr_2 = BaggingRegressor(regr_2_bknn, n_estimators=100)
                            regr_2.label = "Bagging kNN"
                            regr_2.fit(X_tra, y_tra)
                            regr_2.y_val = regr_2.predict(X_val)
                            metricf(y_val, regr_2)
                            metricarf(metdf, metricvf(regr_2))
                            X_ts = dsta_nulls[x_fld]
                            y_t1 = regr_1.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_1.X_tgt = X_ts.copy()
                            regr_1.y_hat = pd.Series(y_t1, index=regr_1.X_tgt.index).copy() if (len(y_t1) > 0) else pd.Series().copy()
                            y_t2 = regr_2.predict(X_ts.values.reshape(-1, 1)) if (X_ts.shape[0] > 0) else X_ts.values.reshape(-1, 1)
                            regr_2.X_tgt = X_ts.copy()
                            regr_2.y_hat = pd.Series(y_t2, index=regr_2.X_tgt.index).copy() if (len(y_t2) > 0) else pd.Series().copy()
                            smo[progn][n_fld][y_dep] = metricamaper2f(dsta[x_fld], dsta[y_dep], regr_1, regr_2)
                            # print("===", progn, n_fld, y_dep, "VARIANTE", smo[progn][n_fld][y_dep].label, "===")
                            # # metdf = metdf.style.apply(highlight_rmse, subset="RMSE", color="lightgreen").apply(highlight_r2, subset="R2", color="lightgreen").highlight_min(subset=["WMAPE"], color="lightblue")
                            # display(metdf)
                            #
                    # else:
                    #     print("=" * 68)
                    #     print("||", n_fld, "EXCLUIDO DE REGRESIÓN POR K NEAREST NEIGHBORS (kNN)")
                    #     print("=" * 68)
                    #     print("||", y_dep, "VALORES EN TOTAL:", dsta_nonulls.shape[0] + dsta_nulls.shape[0])
                    #     print("||", y_dep, "TOTAL VALORES NULOS:", dsta_nulls.shape[0])
                    #     print("=" * 68)
                        #*# ENDFOR FEATURES
                
            # -------------------------------
            smo[self.name][method][algorm] = True
            print("[", algorm, ", done. ]")
        else:
            print("[", algorm, "already done. ]")
        return smo


    def did_fill_w_kneighbors(self, smo):
        # Private constants by method and algo
        method = "fill"
        algorm = "kneighbors"
        # Look into structure
        if (self.name in smo):
            if (method in smo[self.name]):
                if (algorm not in smo[self.name][method]):
                    return False
            else:
                return False
        else:
            return False
        # Look algo's value
        if not smo[self.name][method][algorm]:
            return False
        else:
            return True


    def best_fit_to_fill(self, smo, x_flr, station=None):
        hdf = metricdff(columns = ["PROG", "STATION", "FEATURE", "MODEL", "MAE", "MSE", "RMSE", "MEDAE", "R2", "MAPE", "WMAPE"])
        nfindsf(hdf, smo, self.prognl)
        hdf = hdf.sort_values(by=["STATION", "FEATURE", "WMAPE"], ignore_index=True)
        hdf.drop_duplicates(subset=["STATION", "FEATURE"], inplace=True)
        # curr_max_rows = pd.options.display.max_rows
        # pd.set_option('display.max_rows', None)
        # display(hdf)
        # pd.set_option('display.max_rows', curr_max_rows)
        print(hdf.info())
        print(hdf)
        for idx, row in hdf[["PROG", "STATION", "FEATURE"]].iterrows():
            # print("===", row["PROG"], row["STATION"], row["FEATURE"], end =": ")
            # Filling nulls w/ selected model (Begin)
            smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled = smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_src.copy()
            # print(smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled.count(), end =", ")
            smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled[smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled.isnull()] = smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_hat[smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled.isnull()]
            # print(smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled.count(), end =", ")
            smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie = pd.concat([smo[row["PROG"]][row["STATION"]][row["FEATURE"]].X_src, smo[row["PROG"]][row["STATION"]][row["FEATURE"]].y_filled], axis=1)
            # print(smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie.shape, "===")
            # Filling nulls w/ selected model (End)
        smo["full"] = pd.DataFrame()
        swfullst = ""
        swfull = pd.DataFrame()
        # Fill smo["full"] with smo[prog][station][features]
        for idx, row in hdf[["PROG", "STATION", "FEATURE"]].iterrows():
            # if smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie.shape[1] > 1:
            smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie = smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie.set_index(smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie.columns[0])
            if swfullst != row["STATION"]:
                smo["full"] = pd.concat([smo["full"], swfull])
                swfullst = row["STATION"]
                swfull = pd.DataFrame()
                swfull["date"] = smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie.index
                swfull[x_flr] = row["STATION"]
                swfull = swfull.set_index(swfull.columns[0])
                #
            swfull = pd.merge(swfull, smo[row["PROG"]][row["STATION"]][row["FEATURE"]].dfSerie, how="outer", left_index=True, right_index=True)
            #
        smo["full"] = pd.concat([smo["full"], swfull])
        print("[ Last chunk shape: ", swfull.shape, "]")
        print("[ Full shape: ", smo["full"].shape, "]")
        # Drop remainders
        if (station is not None):
            smo["full"] = smo["full"][smo["full"][x_flr] == station.upper()].copy()
            smo["full"].dropna(how='all', axis=1, inplace=True)
            cols_list = smo["full"].select_dtypes(include = np.number).columns.tolist()
            #
        smo["full"].dropna(inplace=True)
        print("[ Full dropped shape: ", smo["full"].shape, "]")
        print(smo["full"].info())
        print(smo["full"]["station"].unique())
        return smo, cols_list


    def station_auto_init(self, smo, station, cols_list_raw):
        # if ("cache" not in smo):
        #     smo["cache"] = dict()
        #     #
        cols_list = cols_list_raw.copy()
        if (station not in smo["cache"]):
            smo[self.name] = dict()
            for method in self.methal.keys():
                smo[self.name][method] = dict()
                for algorm in self.methal[method]:
                    smo[self.name][method][algorm] = False
                    #
            smo["full"] = dict()
        else:
            smo[self.name] = smo["cache"][station][self.name].copy()
            smo["full"] = smo["cache"][station]["full"].copy()
            cols_list = smo["cache"][station]["cols_list"].copy()
            #
        return smo, cols_list


    def station_auto_save(self, smo, station, cols_list):
        # if ("cache" not in smo):
        #     smo["cache"] = dict()
        #     #
        if (station not in smo["cache"]):
            smo["cache"][station] = dict()
            smo["cache"][station][self.name] = dict()
            smo["cache"][station]["full"] = dict()
            smo["cache"][station]["cols_list"] = None
            #
        smo["cache"][station][self.name] = smo[self.name].copy()
        smo["cache"][station]["full"] = smo["full"].copy()
        smo["cache"][station]["cols_list"] = cols_list.copy()
        return smo


    def drop_features(self, smo, cols_list, n_comp):
        for nc in n_comp:
            if (nc in cols_list):
                smo["full"].drop(columns=nc, inplace=True)
                #
        cols_list = smo["full"].select_dtypes(include = np.number).columns.tolist()
        return smo, cols_list


# UNIT TESTING SECTION

if __name__ == "__main__":
    gReMain = GenRedo()
