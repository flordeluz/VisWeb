# VisWeb

## Changelog

- The new API centralizes all the backend processing

## TODO:

- [x] Improve the method to keep changes in visualization
- [x] Complete Fourier Analysis of cyclicity
- [x] Complete data filter: weekly, monthly (currently not included in this version)
- [x] Show progress bar when loading data
- [x] Show message to make sure the quality of the Data
- [x] Add original data
- [x] Put max points in the cyclicity operator
- [x] Add a spiral graph to cyclicity
- [ ] Close an operator
- [x] Feature discovery
- [x] Informative tooltip topics
- [x] Legend
- [ ] Import/Export data

## BUGS:

- [x] Past and Future Tables names and actions
- [x] Dim. Red changes dropdown of features
- [x] Return to kpadding breaks everything
- [x] Legendre needs limits when there are nulls in very long periods (smoothed Legendre)
- [x] The polygon with more than three dimensions needs to be fixed


## Run the new API server

A new structure for datasets has been developed. See SPECS.pdf or SPECS.org for details.

The easiest way to run the software is by installing the full Anaconda distribution. If you don't want to use the Anaconda's base environment directly, clone it (backup locally and import). After the installation run the Anaconda prompt application from the desired environment, which will allow you to use the Python version provided by Anaconda. Finally, go to the new_api folder (cd command) and install the dependencies:

`cd new_api && pip install -r requirements.txt`

Then, start the server with:

`python main.py`


## Run the Client

Go to the web folder and install dependencies with the following:

`cd web && npm install`

Then, start the client with:

`npm run serve`
