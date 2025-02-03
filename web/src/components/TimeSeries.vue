<template>
<v-container fluid>
  <div class="text-center load-layer" v-if="loading_data">
    <v-progress-circular :size="100" class="loader" color="primary" indeterminate>
      Loading data...
    </v-progress-circular>
  </div>
  <v-row justify="center" dense>
    <v-col class="text-center text-h4 text-capitalize">Dataset: {{ this.dataset }} - {{ this.station }}</v-col>
  </v-row>
  <v-row v-if="chart" justify="center" dense>
    <v-col class="text-center text-h5 text-capitalize">Interval: {{ this.minX }} - {{ this.maxX }}</v-col>
  </v-row>
  <v-row justify="center" dense>
    <v-col cols="10">
      <div id="graph1" class="firstRow graphOne" ref="timeChart" :diameter="200"></div>
    </v-col>
  </v-row>
</v-container>
</template>

<!-- <style> -->
<!-- @import "~metrics-graphics/dist/metricsgraphics.css"; -->
  <!-- </style> -->
 
<script>
// -*- mode: JavaScript -*-
import { AppBus } from '../appBus';
// import MG from "metrics-graphics"
import axios from "axios"
// import Spiral from "@/views/point_spiral"

let CanvasJS = window.CanvasJS

// // import Diagram from "../components/Diagram.vue"
// // import OperatorDiagram from "../components/OperatorDiagram.vue"
// import FeatureViscovery from "feature-viscovery"
// import LeaderLine from "leader-line-new"
// // import tippy from "tippy.js"
// // import "tippy.js/dist/tippy.css" // optional for styling
// import "feature-viscovery/dist/feature-viscovery.esm.css" // optional for styling
// // import Operations from "../components/Operations.vue"

export default {
    components: { /* Diagram, OperatorDiagram, FeatureViscovery */ },
    data: () => ({
	dataset: "",
	station: null,
	// recommendations: {},
	// algorithms: {},
	// tareasHechas: [],
	// reUpdateMacroTask: [],
	chart: null,
	minX: null,
	maxX: null,
	strDates: [],
	// tempMaxData: [],
	// tempMinData: [],
	// precipitationData: [],
	// seePresentChart: false,
	// operation: {},
	// history: [],
	// dialog: false,
	// isClean: false,
	// isCleanFT: false,
	// n_comp: "",
	// factor: "",
	// feature: "",
	// main_operation: "",
	// main_opName: "",
	// main_method: "",
	// newTask: "",
	// pastTable: [],
	// futureTable: [],
	// infoOperation: "",
	// tableIdLines: [],
	// tableLines: [],
	// linesGravity: 50,
	// reduceSelected: false,
	// features: [],
	legends: [],
	loading_data: true,
    }),
    //props: ["dataset", "station", "recommendations"],
    props: [],
    watch: {
	// dataset: function (newValue, oldValue) {
	dataset: function (newValue) {
	    // this.seePresentChart = false;
	    console.log("[ Dataset Name ]:", newValue);
	    // console.log("[ Last Dataset Name ]:", oldValue);
	    console.log("[ Dataset Station Name ]:", this.station);
	    axios
		.get(`http://localhost:8080/data/${newValue}/${this.station}`)
		.then(async data => {
		    let raw_data = data.data;
		    await this.disaggregateData(raw_data);
		    console.log("[ Data Station Length ]: ", raw_data.length);
		    if ( this.chart == null) {
			console.log("[ Chart is Null yet ]");
		    } else {
			this.chart.render();
			console.log("[ Chart Rendered ]");
		    }
		    // this.history = [];
		})
	},
    },
    methods: {
	handleRangeChange(e) {
	    const axisX = e.axisX[0];
	    if ( axisX.viewportMinimum == null || axisX.viewportMaximum == null) {
		this.minX = this.strDates[0];
		this.maxX = this.strDates[this.strDates.length-1];
	    } else {
		this.minX = this.strDates[Math.floor(Math.abs(axisX.viewportMinimum))];
		this.maxX = this.strDates[Math.floor(Math.abs(axisX.viewportMaximum))];
	    }
	},
	minmaxInterval(raw_data) {
	    let min_value = 0;
	    let max_value = 0;
	    let vis_scale = 100;
	    let vis_sizes = { 10: 1, 100: 5, 1000: 10, 10000: 50 }
	    raw_data.forEach(sample => {
		for (const [key, value] of Object.entries(sample)) {
		    if (key !== "date" && value) {
			if (min_value > value) min_value = value;
			if (max_value < value) max_value = value;
		    }
		}
	    });
	    let vis_dif = max_value - min_value;
	    for (const [vis_key, vis_val] of Object.entries(vis_sizes)) {
		if ( vis_dif < vis_key ) {
		    vis_scale = vis_val;
		    break;
		}
	    }
	    console.log("[ Min and Max Chart Values ]: (", min_value, ",", max_value, ")");
	    if ( min_value < 0 ) {
		min_value = Math.ceil(Math.abs(min_value) / vis_scale) * -vis_scale;
	    } else if ( min_value > 0 ) {
		min_value = Math.floor(min_value / vis_scale) * vis_scale;
	    }
	    if ( max_value < 0 ) {
		max_value = Math.floor(Math.abs(max_value) / vis_scale) * -vis_scale;
	    } else if ( max_value > 0 ) {
		max_value = Math.ceil(max_value / vis_scale) * vis_scale;
	    }
	    console.log("[ Interval Chart Values ]: [", min_value, ",", max_value, "]")
	    return [ min_value, max_value ];
	},
	async disaggregateData(raw_data) {
	    console.log("[ Raw Data to Split: ]", raw_data, typeof raw_data)
	    if ( typeof raw_data === "string" ) raw_data = JSON.parse(raw_data)
	    // console.log("[ Disaggregate: Any ]:", this.operation.operation_name)
	    // this.tempMaxData = await raw_data.map (
	    // 	({ date: label, tempMax: y }) => ({ label, y })
	    // )
	    // this.tempMinData = await raw_data.map (
	    // 	({ date: label, tempMin: y }) => ({ label, y })
	    // )
	    // this.precipitationData = await raw_data.map (
	    // 	({ date: label, precipitation: y }) => ({ label, y })
	    // )
	    let keys = Object.keys(raw_data[0])
	    keys.splice(keys.indexOf("date"), 1)
	    let resData = []
	    console.log("[ KEYS ]", keys)
	    keys.forEach(async key => {
		let feature_points = await raw_data.map (
		    day_data => ({ label: day_data.date, y: day_data[key] })
		)
		resData.push ({
		    datapoints: feature_points,
		    name: key
		})
	    })
	    this.legends = keys
	    return resData
	}
    },
    mounted: function () {
	// this.isClean = false
	// this.isCleanFT = false
	// this.algorithms = {}
	this.dataset = this.$route.params.dataset
	this.station = this.$route.params.station
	AppBus.$emit('disabled-buttons', false);
	AppBus.$emit('update-button-home', false, true);
	AppBus.$emit('update-button-assets', false, true);
	AppBus.$emit('update-button-net', false, true);
	AppBus.$emit('update-button-visualize', true, false);
	AppBus.$emit('update-button-stats', false, true);
	AppBus.$emit('update-button-spiral', false, true);
	document.getElementById("dynAssets").href=`/assets/${this.dataset}/${this.station}`;
	document.getElementById("dynNet").href=`/net/${this.dataset}/${this.station}`;
	document.getElementById("dynVisualize").href=`/visualize/${this.dataset}/${this.station}`;
	document.getElementById("dynStats").href=`/stats/${this.dataset}/${this.station}`;
	document.getElementById("dynSpiral").href=`/spiral/${this.dataset}/${this.station}`;
	// this.getRecommendations(this.dataset, this.station)
	// console.log("[ Time Series ]", this.dataset, this.station, this.recommendations)
	axios
	    .get(`http://localhost:8080/data/${this.dataset}/${this.station}`)
	    .then(async data => {
		let raw_data = data.data;
		// CHART: creating new chart with disaggregated sep_data
		console.log("[ Mounted Raw Data Length ]:", raw_data.length);
		const [ interval_start, interval_end ] = this.minmaxInterval(raw_data);
		this.minX = raw_data[0].date;
		this.maxX = raw_data[raw_data.length-1].date;
		for (const key in raw_data) {
		    this.strDates[key] = raw_data[key].date;
		}
		console.log("[ Mounted Dates ]: ", this.strDates);
		let sep_data = await this.disaggregateData(raw_data);
		console.log("[ Mounted Split Data ]: ", sep_data);
		console.log("[ Mounted Split Data Length ]:", sep_data.length);
		console.log("[ Mounted Interval Chart Values ]: [", interval_start, ",", interval_end, "]");
		this.chart = new CanvasJS.Chart("graph1", {
		    animationEnabled: true,
		    exportEnabled: true,
		    zoomEnabled: true,
		    // width: 1072, // commented
		    // height: 580,
		    axisX: {
			labelFontSize: 18,
			labelAngle: -45,
			intervalType: "day"
		    },
		    axisY: {
			labelFontSize: 18,
			// labelAngle: -45,
			viewportMinimum: interval_start,
			viewportMaximum: interval_end
		    },
		    title: {
			// text: `Dataset Length: ${this.precipitationData.length}, ${raw_data.length}`
			fontSize: 24,
			text: `Dataset Length: ${raw_data.length}`
		    },
		    legend: {
			cursor: "pointer",
			verticalAlign: "top",
			fontSize: 18,
			fontColor: "dimGrey"
		    },
		    data: sep_data.map(feat_data => ({
			type: "line",
			xValueType: "dateTime",
			name: feat_data.name,
			showInLegend: true,
			lineThickness: 1.4,
			dataPoints: feat_data.datapoints
		    }))
		});
		this.chart.options.rangeChanged = this.handleRangeChange;
		this.chart.render();
		this.loading_data = false;
		console.log("[ Viewports X ]:", this.minX, this.maxX);
	    });
    }
}
</script>

<style>
td.rotate-text {
    transform: rotate(90deg);
}
table.blockTable {
    writing-mode: vertical-lr;
    min-width: 50px;
    /* for firefox */
}
.firstRow {
    height: 66vh;
}
/* table.pastTable { */
/*     margin-left: auto; */
/* } */
td.slideOp:hover {
    background-color: rgba(6, 10, 223, 0.109);
    cursor: pointer;
}
div.load-layer {
    background-color: #efefef;
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 1000;
    top: 0px;
    left: 0px;
    opacity: 0.8;
    /* in FireFox */
    filter: alpha(opacity=80);
    /* in IE */
}
.loader {
    top: 20%;
}
.theme--light.application.autoaim {
    background-image: linear-gradient(60deg, #64b3f4 0%, #c2e59c 100%) !important;
}
.graphOne {
    height: 76vh;
    width: 100%; /* 1080px; */
    position: relative;
    border: 3px solid #8FBC8F; /* #73AD21; */
    border-radius: 6px;
}
</style>
