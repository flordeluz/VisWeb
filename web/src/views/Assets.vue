<template>
<v-container class="my-6" fluid>
  <v-row dense align="center" justify="center">
    <h3><b>Available Datasets</b></h3>
  </v-row>
  <v-row dense align="center" justify="center">
    <ul>
      <li v-for="file in fileList" :key="file">{{ file }}</li>
    </ul>
  </v-row>
  <v-row dense class="vhrow" align="center" justify="center"/>
  <v-row dense align="center" justify="center">
    <h3><b>Import Dataset from CSV File</b></h3>
  </v-row>
  <v-row dense align="center" justify="space-between">
    To import your CSV file correctly, the first row must contain column headers, and at least one column must be a date type (in days). If multiple date columns exist, the first one from the left will be used as the key. Column names are not required, but the key date column will be automatically renamed 'date.'
  </v-row>
  <v-row dense align="center" justify="space-between">
    You may also include a special column called 'station.' If your dataset lacks this column, it will be created automatically based on the dataset name. If present, the 'station' column will be used to group and analyze data by station.
  </v-row>
  <v-row dense align="center" justify="center">
    <v-col cols="5" align="center" justify="center">
      <b>Example 1: ASSET1.csv</b>
      <table class="w-full border border-gray-300">
        <thead class="bg-gray-200">
          <tr>
	    <th v-for="header in asset1Headers" :key="header" class="border p-2">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in asset1Data" :key="index" class="border">
	    <td v-for="(value, key) in row" :key="key" class="border p-2">{{ value }}</td>
          </tr>
        </tbody>
      </table>
    </v-col>
    <v-col cols="5" align="center" justify="center">
      <b>Example 2: MULTIPLE-ASSETS.csv</b>
      <table class="w-full border border-gray-300">
        <thead class="bg-gray-200">
          <tr>
	    <th v-for="header in multiAssetHeaders" :key="header" class="border p-2">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in multiAssetData" :key="index" class="border">
	    <td v-for="(value, key) in row" :key="key" class="border p-2">{{ value }}</td>
          </tr>
        </tbody>
      </table>
    </v-col>
  </v-row>
  <v-row dense align="center" justify="center">
    <v-col cols="3" align="center" justify="center">
      <input v-model="customFilename" placeholder="Optional dataset name" />
    </v-col>
    <v-col cols="3" align="center" justify="center">
      <input type="file" @change="handleFileUpload" accept=".csv" />
    </v-col>
    <v-col cols="3" align="center" justify="center">
      <button @click="uploadFile">Upload</button>
    </v-col>
  </v-row>
  <v-row dense class="vhrow" align="center" v-if="station" justify="center"/>
  <v-row dense align="center" v-if="station" justify="center">
    <h3><b>Export Dataset to CSV File</b></h3>
  </v-row>
  <v-row dense align="center" v-if="station" justify="center">
    <button @click="exportFile">Export</button>
  </v-row>
  <v-row dense class="vhrow" align="center" v-if="message" justify="center"/>
  <v-row v-if="message" class="message" justify="center">
    <h5><b>{{ message }}</b></h5>
  </v-row>
  <v-row dense class="vhrow" align="center" v-if="information" justify="center"/>
  <v-row v-if="information" class="information" justify="center">
    <h5><b>{{ information }}</b></h5>
  </v-row>
</v-container>
</template>

<script>
// -*- mode: JavaScript -*-
import { AppBus } from '../appBus';
import axios from "axios"
import "@/views/bootstrap.min.css"
export default {
    name: "Assets",
    data: () => ({
	dataset: "",
	station: null,
	fileList: [],
	selectedFile: null,
	customFilename: '',
	message: '',
	information: '',
	asset1Headers: ["Date", "Price", "Open", "Vol.", "Change %"],
	asset1Data: [
            { Date: "02/10/2025", Price: "96,947.0", Open: "96,469.2", "Vol.": "53.83K", "Change %": "0.50%" },
            { Date: "02/09/2025", Price: "96,469.2", Open: "96,448.4", "Vol.": "48.38K", "Change %": "0.02%" },
            { Date: "02/08/2025", Price: "96,447.9", Open: "96,513.5", "Vol.": "38.99K", "Change %": "-0.07%" },
	],
	multiAssetHeaders: ["Date", "Price", "Open", "Vol.", "Change %", "Station"],
	multiAssetData: [
            { Date: "02/10/2025", Price: "96,947.0", Open: "96,469.2", "Vol.": "53.83K", "Change %": "0.50%", Station: "Asset1" },
            { Date: "02/09/2025", Price: "96,469.2", Open: "96,448.4", "Vol.": "48.38K", "Change %": "0.02%", Station: "Asset1" },
            { Date: "02/10/2025", Price: "69,148.0", Open: "71,627.3", "Vol.": "93.69K", "Change %": "-3.47%", Station: "Asset2" },
            { Date: "02/09/2025", Price: "71,630.1", Open: "69,358.0", "Vol.": "105.78K", "Change %": "3.27%", Station: "Asset2" },
	]
    }),
    methods: {
	async fetchFiles() {
	    try {
		const response = await axios.get('http://localhost:8080/assets/getfiles');
		this.fileList = response.data;
		console.log("[ response ]:", this.fileList);
	    } catch (error) {
		this.message = 'Error fetching file list.';
		this.information = '';
	    }
	},
	handleFileUpload(event) {
	    this.selectedFile = event.target.files[0];
	},
	async uploadFile() {
	    if (!this.selectedFile) {
		this.message = 'Please select a file first.';
		this.information = '';
		return;
	    }
	    
	    const formData = new FormData();
	    let filename = this.customFilename.trim() || this.selectedFile.name.split('.').slice(0, -1).join('.');
	    formData.append('file', this.selectedFile);
	    formData.append('filename', filename);
	    
	    try {
		const response = await axios.post('http://localhost:8080/assets/importfile', formData, {
		    headers: { 'Content-Type': 'multipart/form-data' }
		});
		this.information = response.data.message || 'File uploaded.';
		this.message = '';
		this.fetchFiles(); // Refresh file list
	    } catch (error) {
		this.message = 'Error uploading file.';
		this.information = '';
	    }
	},
	async exportFile() {
	    try {
		const response = await axios.get('http://localhost:8080/assets/exportfile/' + this.dataset + '/' + this.station, { responseType: 'blob' });
		
		const url = window.URL.createObjectURL(new Blob([response.data]));
		const link = document.createElement('a');
		link.href = url;
		link.setAttribute('download', this.dataset + '_' + this.station + '.csv');
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		AppBus.$emit('data-changed', false);
	    } catch (error) {
		this.message = 'Error exporting file.';
		this.information = '';
	    }
	}
    },
    mounted: function() {
	this.dataset = this.$route.params.dataset;
	this.station = this.$route.params.station;
	if (this.station == null) {
	    AppBus.$emit('disabled-buttons', true);
	} else {
	    AppBus.$emit('disabled-buttons', false);
	}
	AppBus.$emit('update-button-home', false, true);
	AppBus.$emit('update-button-assets', true, false);
	AppBus.$emit('update-button-net', false, true);
	AppBus.$emit('update-button-visualize', false, true);
	AppBus.$emit('update-button-stats', false, true);
	AppBus.$emit('update-button-spiral', false, true);
	if (this.station != null) {
	    document.getElementById("dynAssets").href=`/assets/${this.dataset}/${this.station}`;
	    document.getElementById("dynNet").href=`/net/${this.dataset}/${this.station}`;
	    document.getElementById("dynVisualize").href=`/visualize/${this.dataset}/${this.station}`;
	    document.getElementById("dynStats").href=`/stats/${this.dataset}/${this.station}`;
	    document.getElementById("dynSpiral").href=`/spiral/${this.dataset}/${this.station}`;
	}
	this.fetchFiles();
    }
};
</script>

<style>
/* .container { */
/*     max-width: 600px; */
/*     margin: auto; */
/*     text-align: center; */
/* } */
.container {
    padding: 20px;
    font-size: 10pt; 
    font-family: sans-serif;
    border-collapse: collapse; 
    border: 2px solid lightgray; /* silver */
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
.message {
    background-color: #DFEFFF;
    /* border: 2px solid lightgray; */
    padding: 10px;
    font-size: 10pt; 
    font-family: sans-serif;
    border-radius: 5px;
    text-align: left;
    word-wrap: break-word;
    white-space: pre-line;  
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-top: 10px;
    color: red;
}
.information {
    background-color: #DFEFFF;
    /* border: 2px solid lightgray; */
    padding: 10px;
    font-size: 10pt; 
    font-family: sans-serif;
    border-radius: 5px;
    text-align: left;
    word-wrap: break-word;
    white-space: pre-line;  
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-top: 10px;
    color: green;
}
button {
    padding: 5px;
    min-width: 100px;
    border-collapse: collapse; 
    border: 2px solid lightblue;
    background-color: #DFEFFF;
}
input {
    padding: 5px;
    border-collapse: collapse; 
    border: 2px solid lightblue;
}
.vhrow {
    padding: 20px;
    border-bottom: solid 1px #DFEFFF;
}
table {
    border-collapse: collapse;
}
th, td {
    padding: 1px;
    text-align: left;
}
th {
    background-color: #DFEFFF;
}
</style>
