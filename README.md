# VisWeb

## TODO:

- [x] Improve the method to keep changes on visualization
- [x] Complete Fourier Analysis of cyclicity
- [x] Complete data filter: weekly, monthly (currently not included in this version)
- [x] Show progress bar when load data
- [x] Show message to make sure the quality of Data
- [x] Add original data
- [ ] Support multiple arrows from Operator box to Op tables
- [ ] Put max points in ciclicity operator
- [ ] Add spiral graph to ciclicity
- [ ] Close an operator
- [ ] Feature discovery
- [ ] Resaltar

## BUGS:

- [x] Past and Future Tables names and actions
- [x] Dim. Red changes dropdown of features
- [x] Return to kpadding breaks everything

## Note:

There's new JS libraries included in the project, please install new dependencies running on `VisWeb/web` folder

`npm install`

## Run the API server

Before this, you should extract the .rar file `Datos.rar`

Go to the api folder and install dependencies:

`cd api && pip3 install -r requirements.txt`

Then, start the server with:

`python3 main.py`

## Run the Client

Go to the web folder and install dependencies with:

`cd web && npm install`

Then, start the client with:

`npm run serve`
