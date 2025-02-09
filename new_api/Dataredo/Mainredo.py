# -*- mode: python -*-
#
# Copyright (C) 2024  Victor C. Salas P.
#
# Author: Victor C. Salas P. <nmagko@gmail.com>

from pandas import DataFrame

class MainredoClass:
    def __init__(self) -> None:
        pass

    def iqr_treatment(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_iqr_treatment(self, smo) -> bool:
        pass

    def reset_iqr_treatment(self, smo) -> bool:
        pass

    def sdv_treatment(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_sdv_treatment(self, smo) -> bool:
        pass

    def reset_sdv_treatment(self, smo) -> bool:
        pass

    def set_interval(self, minx, maxx, smo) -> dict:
        pass

    def linear_transform(self, num, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_linear_transform(self, smo) -> bool:
        pass

    def quadratic_transform(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_quadratic_transform(self, smo) -> bool:
        pass

    def log_transform(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_log_transform(self, smo) -> bool:
        pass

    def sqrt_transform(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_sqrt_transform(self, smo) -> bool:
        pass
    
    def diff_transform(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_diff_transform(self, smo) -> bool:
        pass
    
    def norm_w_maxabs(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_norm_w_maxabs(self, smo) -> bool:
        pass

    def norm_w_minmax(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_norm_w_minmax(self, smo) -> bool:
        pass

    def norm_w_standard(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_norm_w_standard(self, smo) -> bool:
        pass
    
    def norm_w_robust(self, ds, smo, cols_list) -> (DataFrame, dict):
        pass

    def did_norm_w_robust(self, smo) -> bool:
        pass

    def fill_w_meanmedian(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_meanmedian(self, smo) -> bool:
        pass

    def fill_w_decisiontree(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_decisiontree(self, smo) -> bool:
        pass

    def fill_w_gradientboosting(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_gradientboosting(self, smo) -> bool:
        pass

    def fill_w_locallyweighted(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_locallyweighted(self, smo) -> bool:
        pass

    def fill_w_legendre(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_legendre(self, smo) -> bool:
        pass

    def fill_w_randomforest(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_randomforest(self, smo) -> bool:
        pass

    def fill_w_kneighbors(self, ds, smo, minsample, valdnsize, x_flr, cols_list, time_list) -> dict:
        pass

    def did_fill_w_kneighbors(self, smo) -> bool:
        pass

    def best_algo_metrics(self, smo) -> DataFrame:
        pass

    def best_fit_to_fill(self, smo, x_flr) -> dict:
        pass

    def station_auto_init(self, smo, station) -> dict:
        pass

    def station_auto_save(self, smo, station) -> dict:
        pass

    def drop_features(self, smo, cols_list, n_comp) -> (dict, list):
        pass
