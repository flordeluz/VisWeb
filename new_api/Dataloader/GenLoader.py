# -*- mode: python -*-
#
# Copyright (C) 2024  Victor C. Salas P.
#
# Author: Victor C. Salas P. <nmagko@gmail.com>

from .Mainloader import MainloaderClass
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import glob
import os
import sys
import re

# CLASS DEFINITION

class GenLoader(MainloaderClass):
    # .ds: Active Dataframe
    # .smo["raw"]: Copy of the original .ds Dataframe
    # .smo["maxabs"] .smo["minmax"] .smo["standard"]: Normalized/Scaled Dataframe
    # .smo["full"]: Filled raw Dataframe
    def __init__(self, path: str):
        super().__init__(path)
        print("[ Loading data source:", path, "]")
        # Objects, Variables, and Global Constants
        # -------------------------------
        self.have_nulls = False
        self.epsilon = sys.float_info.epsilon
        self.dpi = 100
        self.smo = dict()
        self.minsample = 10
        self.valdnsize = 1/self.minsample
        # -------------------------------
        self.data = pd.DataFrame()
        self.read()


    def read(self):
        # HINT: Multiple Data Sources Pre-Process
        # -------------------------------
        # PRE-PROCESS MSG: In the future this section will be the driver loader.
        # PRE-PROCESS MSG: It will understand the path ending with / as a folder
        # PRE-PROCESS MSG: otherwise the path will be a file.
        # PRE-PROCESS MSG: In case of a folder it has to determine if it contains
        # PRE-PROCESS MSG: plain text files or compressed files.
        # PRE-PROCESS MSG: It has to read a config file to determine field names
        # PRE-PROCESS MSG: and types, depending on the source. This can be train
        # PRE-PROCESS MSG: in an ANN to generalize sources with common structures.
        if re.match(r".*\.data\/India", self.path): # India Driver
            self.data = pd.read_csv(self.path, low_memory=False)
            self.ds = self.data
            self.ds["Date"] = pd.to_datetime(self.ds["Date"], format = "%Y-%m-%d")
            self.freq = "D"
            self.y_dep = "AQI"
            #
        elif re.match(r".*\.data\/Madrid", self.path): # Madrid Driver
            all_files = glob.glob(os.path.join(self.path, "*.csv"))
            self.data = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
            self.ds = self.data
            self.ds["date"] = pd.to_datetime(self.ds["date"], format = "%Y-%m-%d %H:%M:%S")
            self.freq = "h"
            self.y_dep = "CO"
            #
        elif re.match(r".*\.data\/Peru", self.path): # Peru Driver
            all_files = glob.glob(os.path.join(self.path, "*.txt"))
            i = 0
            dt = []
            for f in all_files:
                dt.append(pd.read_csv(f, header = None, delimiter = " "))
                va = re.sub(r"^.*/", "", f)
                va = re.sub(r"\.txt$", "", va)
                dt[i]["station"] = va
                i += 1
                #
            self.data = pd.concat((d for d in dt), ignore_index=True)
            self.ds = self.data
            self.ds["Date"] = pd.to_datetime(self.ds[0].astype(str) + self.ds[1].astype(str).str.zfill(2) + self.ds[2].astype(str).str.zfill(2), format = "%Y%m%d")
            self.ds.rename(columns={3:"PPT", 4:"TXM", 5:"TNM"}, inplace = True)
            self.ds = self.ds[["Date", "PPT", "TXM", "TNM", "station"]]
            self.ds = self.ds.replace(-99.9, np.NaN)
            self.freq = "D"
            self.y_dep = "PPT"
            #
        elif re.match(r".*\.data\/Brasil", self.path): # Brasil Driver
            all_files = glob.glob(os.path.join(self.path, "*.gz"))
            self.data = pd.concat((pd.read_csv(f, compression="gzip") for f in all_files), ignore_index=True)
            self.ds = self.data
            self.ds["hour"] -= 1
            self.ds["Date"] = pd.to_datetime(self.ds["date"].astype(str) + self.ds["hour"].astype(str).str.zfill(2), format = "%Y-%m-%d%H")
            self.ds = self.ds[["Date", "stationname", "parameter", "conc"]]
            self.ds = self.ds.pivot(index=["Date", "stationname"], columns="parameter", values="conc").reset_index()
            self.freq = "D"
            self.y_dep = "TEMP"
            #
        self.x_flr = "station"
        self.ds.rename(columns = {"Date":"date", "StationId":self.x_flr, "stationname":self.x_flr}, inplace = True)
        self.ds[self.x_flr] = self.ds[self.x_flr].astype(str)
        self.ds[self.x_flr] = self.ds[self.x_flr].str.upper()
        dFrm = pd.DataFrame()
        for s_flr in self.ds[self.x_flr].unique():
            dSer = pd.Series(pd.date_range(min(self.ds[self.ds[self.x_flr] == s_flr]["date"]), max(self.ds[self.ds[self.x_flr] == s_flr]["date"]), freq=self.freq), name="date")
            dFra = pd.DataFrame()
            dFra["date"] = dSer
            dFra[self.x_flr] = s_flr
            dFrm = pd.concat([dFrm, dFra])
            #
        self.ds = pd.merge(self.ds, dFrm, how="outer", left_on=["date", self.x_flr], right_on=["date", self.x_flr])
        # -------------------------------
        self.cols_list = self.ds.select_dtypes(include = np.number).columns.tolist()
        self.cols_list_raw = self.cols_list.copy()
        self.catg_list = self.ds.select_dtypes(exclude = [np.number, np.datetime64, np.timedelta64]).columns.tolist()
        # HINT: The time_list may have multiple time fields. We use the first one [0] as a key for indexing
        self.time_list = self.ds.select_dtypes(include = [np.datetime64, np.timedelta64]).columns.tolist()
        self.ds.sort_values([self.x_flr] + self.time_list, inplace=True)
        self.stations = list(self.ds[self.x_flr].unique())
        self.smo["raw"] = self.ds.copy() # RAW DATA COPY


    def get_metadata(self):
        meta_data = []
        for station in self.stations:
            station_df = self.ds[self.ds[self.x_flr] == station]
            null_p = (station_df.isnull().sum() / station_df.shape[0])*100
            station_data = {
                "station_name": station,
                "features": list(station_df.columns),
                "null_per": null_p.to_dict(),
                "info": {
                    "Length": station_df.shape[0],
                    # HINT: We use the first one [0] as key and for indexing
                    "Start date": station_df[self.time_list[0]].min().strftime("%Y-%m-%d"),
                    "End date": station_df[self.time_list[0]].max().strftime("%Y-%m-%d")
                },
            }
            meta_data.append(station_data)
        return meta_data


    def get_station_metadata(self, station):
        print("[ Summoned with:", station, "]")
        station_df = self.ds[self.ds[self.x_flr] == station.upper()].copy()
        null_p = (station_df.isnull().sum() / station_df.shape[0])*100
        station_data = {
            "station_name": station,
            "features": list(station_df.columns),
            "null_per": null_p.to_dict(),
            "info": {
                "Length": station_df.shape[0],
                # HINT: We use the first one [0] as key and for indexing
                "Start date": station_df[self.time_list[0]].min().strftime("%Y-%m-%d"),
                "End date": station_df[self.time_list[0]].max().strftime("%Y-%m-%d")
            },
        }
        return station_data


    def get_station_df(self, station_id = None, resample = None, skipna = True):
        # Picking the first station fi none is passed
        if station_id is None:
            station_id = self.stations[0]
            #
        station_data = self.ds[self.ds[self.x_flr] == station_id.upper()].copy()
        full_station_data = station_data.copy()
        # Dropping categorical columns including stations
        # station_data.drop(self.catg_list, axis=1, inplace=True)
        station_data.drop(self.catg_list, axis=1, inplace=True, errors="ignore")
        if self.time_list[0] in station_data.columns:
            station_data.set_index(self.time_list[0], inplace=True)
            #
        if resample is not None: # HINT: Checking if resample was set
            station_data = station_data.resample(resample).agg(pd.Series.median, skipna=skipna)
            #
        station_data.index = pd.to_datetime(station_data.index).strftime("%Y-%m-%d")
        # HINT: We are letting full_station_data with its default index in case it has hours
        # full_station_data.index = pd.to_datetime(full_station_data.index).strftime("%Y-%m-%d")
        # HINT: Format to yyyy-mm-dd because of json takes full timestamp as big int
        return station_data, full_station_data


    def get_data(self, station_id = None, to_json = True, with_df = False, resample = None, skipna = True):
        # Picking the first station fi none is passed
        if station_id is None:
            station_id = self.stations[0]
            #
        station_data, full_station_data = self.get_station_df(station_id, resample = resample, skipna = skipna)
        if not to_json:
            return station_data.to_dict(orient = "records"), station_data, full_station_data
        #
        return station_data.reset_index().to_json(orient = "records"), station_data, full_station_data


    def get_station_raw_df(self, station_id = None, resample = None, skipna = True):
        # Picking the first station fi none is passed
        if station_id is None:
            station_id = self.stations[0]
            #
        station_data = self.smo["raw"][self.smo["raw"][self.x_flr] == station_id.upper()].copy()
        full_station_data = station_data.copy()
        # Dropping categorical columns including stations
        station_data.drop(self.catg_list, axis=1, inplace=True)
        station_data.set_index(self.time_list[0], inplace=True)
        if resample is not None: # HINT: Checking if resample was set
            station_data = station_data.resample(resample).agg(pd.Series.median, skipna=skipna)
            #
        station_data.index = pd.to_datetime(station_data.index).strftime("%Y-%m-%d")
        # HINT: We are letting full_station_data with its default index in case it has hours
        # full_station_data.index = pd.to_datetime(full_station_data.index).strftime("%Y-%m-%d")
        # HINT: Format to yyyy-mm-dd because of json takes full timestamp as big int
        return station_data, full_station_data


    def get_raw_data(self, station_id = None, to_json = True, with_df = False, resample = None, skipna = True):
        # Picking the first station fi none is passed
        if station_id is None:
            station_id = self.stations[0]
            #
        station_data, full_station_data = self.get_station_raw_df(station_id, resample = resample, skipna = skipna)
        # DOES GET RAW DATA IN THE FRONTEND REVERT DS TO SMO["RAW"]? IF SO
        # self.ds = self.smo["raw"].copy() # REVERT TO RAW DATA
        if not to_json:
            return station_data.to_dict(orient = "records"), station_data, full_station_data
        #
        return station_data.reset_index().to_json(orient = "records"), station_data, full_station_data


# UNIT TESTING SECTION

if __name__ == "__main__":
    path = "../.data/India/station_day.csv"
    gLoMain = GenLoader(path)
