# -*- mode: python -*-
#
# Copyright (C) 2024  Victor C. Salas P.
#
# Author: Victor C. Salas P. <nmagko@gmail.com>

from pandas import DataFrame

class MainloaderClass:
    def __init__(self, path: str) -> None:
        self.path = path

    def get_metadata(self) -> list:
        pass

    def get_station_metadata(self, station) -> dict:
        pass

    def get_station_df(self, station_id, resample, skipna) -> (DataFrame, DataFrame):
        pass

    def get_data(self, station_id, to_json, with_df, resample, skipna) -> (str, DataFrame, DataFrame):
        pass

    def get_station_raw_df(self, station_id, resample, skipna) -> (DataFrame, DataFrame):
        pass

    def get_raw_data(self, station_id, to_json, with_df, resample, skipna) -> (str, DataFrame, DataFrame):
        pass
