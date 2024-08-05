<template>
<v-container class="my-6" fluid>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <h2>Dataset: {{ dataset.toUpperCase() }}, Station: {{ station.toUpperCase() }}</h2>
  </v-row>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <v-col cols="10">
      <div v-html="rawcontainer"></div>
    </v-col>
  </v-row>
</v-container>
</template>

<script>
// -*- mode: JavaScript -*-
// import { createNodeImageProgram } from "@sigma/node-image";
import Graph from "graphology";
import ForceLayout from "graphology-layout-force/worker";
// import ForceLayout from "graphology-layout-forceatlas2/worker";
// import ForceLayout from "graphology-layout-noverlap/worker";

import Sigma from "sigma";

import { onStoryDown } from "./utils";
import NodeGradientProgram from "./node-gradient";

// import axios from "axios"
import "@/views/bootstrap.min.css"

export default {
    name: "Network",
    data: () => ({
	dataset: "",
	station: null,
	datasetSelected: false,
	rawcontainer: '<div id="container" style="width: 100vh; height: 80vh; background: #fff;"></div>',
	container: null,
	graph: null,
	renderer: null,
	layout: null,
	RED: "#FA4F40",
	BLUE: "#727EE0",
	GREEN: "#5DB346",
	YELLOW: "#F6F606",
	GRAY: "#767686",
	PROCSZ: 24,
	SUBPSZ: 18,
	ACTVSZ: 12
    }),
    methods: {
	async showNetwork() {
	    this.datasetSelected = true
	    await new Promise(r => setTimeout(r, 2000));
	    this.container = document.getElementById("container")
	    console.log("[ Container ]:", this.container);
	    this.graph = new Graph();
	    
	    // Nodes
	    this.graph.addNode("Data Quality", { size: this.PROCSZ, label: "Data Quality", type: "gradient", color: this.RED });
	    this.graph.addNode("Cleaning", { size: this.SUBPSZ, label: "Cleaning", type: "gradient", color: this.RED });
	    this.graph.addNode("Rolling Mean", { size: this.ACTVSZ, label: "Rolling Mean", type: "gradient", color: this.RED });
	    this.graph.addNode("Decision Tree", { size: this.ACTVSZ, label: "Decision Tree", type: "gradient", color: this.RED });
	    this.graph.addNode("Stochastic Gradient Boosting", { size: this.ACTVSZ, label: "Stochastic Gradient Boosting", type: "gradient", color: this.RED });
	    this.graph.addNode("Locally Weighted Regression", { size: this.ACTVSZ, label: "Locally Weighted Regression", type: "gradient", color: this.RED });
	    this.graph.addNode("Legendre", { size: this.ACTVSZ, label: "Legendre", type: "gradient", color: this.RED });
	    this.graph.addNode("Random Forest Regressor", { size: this.ACTVSZ, label: "Random Forest Regressor", type: "gradient", color: this.RED });
	    this.graph.addNode("KNN", { size: this.ACTVSZ, label: "KNN", type: "gradient", color: this.RED });
	    this.graph.addNode("Normalization", { size: this.SUBPSZ, label: "Normalization", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("MinMax", { size: this.ACTVSZ, label: "MinMax", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Standard", { size: this.ACTVSZ, label: "Standard", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("MaxAbs", { size: this.ACTVSZ, label: "MaxAbs", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Robust", { size: this.ACTVSZ, label: "Robust", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Transform", { size: this.SUBPSZ, label: "Transform", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Linear", { size: this.ACTVSZ, label: "Linear", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Quadratic", { size: this.ACTVSZ, label: "Quadratic", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Square Root", { size: this.ACTVSZ, label: "Square Root", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Logarithm", { size: this.ACTVSZ, label: "Logarithm", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Differencing", { size: this.ACTVSZ, label: "Differencing", type: "gradient", color: this.YELLOW });
	    this.graph.addNode("Data Reduction", { size: this.PROCSZ, label: "Data Reduction", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Dim.Reduction", { size: this.SUBPSZ, label: "Dim.Reduction", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Factor Analysis", { size: this.ACTVSZ, label: "Factor Analysis", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Manually Selected", { size: this.ACTVSZ, label: "Manually Selected", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Behavior", { size: this.PROCSZ, label: "Behavior", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Trend", { size: this.SUBPSZ, label: "Trend", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Cyclicity", { size: this.SUBPSZ, label: "Cyclicity", type: "gradient", color: this.GRAY });
	    this.graph.addNode("Seasonality", { size: this.SUBPSZ, label: "Seasonality", type: "gradient", color: this.GRAY });
	    
	    // Line edges processes
	    this.graph.addEdge("Data Quality", "Data Reduction", { type: "line", label: "process", size: 7 });
	    this.graph.addEdge("Data Reduction", "Behavior", { type: "line", label: "process", size: 7 });
	    this.graph.addEdge("Data Quality", "Behavior", { type: "line", label: "process", size: 7 });

	    // Line edges subprocesses
	    this.graph.addEdge("Data Quality", "Cleaning", { type: "line", label: "subprocess", size: 5, color: this.RED });
	    this.graph.addEdge("Cleaning", "Rolling Mean", { type: "arrow", label: "activity", size: 3, color: this.RED });
	    this.graph.addEdge("Cleaning", "Decision Tree", { type: "arrow", label: "activity", size: 3, color: this.RED });
	    this.graph.addEdge("Cleaning", "Stochastic Gradient Boosting", { type: "arrow", label: "activity", size: 3, color: this.RED });
	    this.graph.addEdge("Cleaning", "Locally Weighted Regression", { type: "arrow", label: "activity", size: 3, color: this.RED });
	    this.graph.addEdge("Cleaning", "Legendre", { type: "arrow", label: "activity", size: 3, color: this.RED });
	    this.graph.addEdge("Cleaning", "Random Forest Regressor", { type: "arrow", label: "activity", size: 3, color: this.RED });
	    this.graph.addEdge("Cleaning", "KNN", { type: "arrow", label: "activity", size: 3, color: this.RED });

	    this.graph.addEdge("Data Quality", "Normalization", { type: "line", label: "subprocess", size: 5, color: this.YELLOW });
	    this.graph.addEdge("Normalization", "MinMax", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Normalization", "Standard", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Normalization", "MaxAbs", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Normalization", "Robust", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    
	    this.graph.addEdge("Data Quality", "Transform", { type: "line", label: "subprocess", size: 5, color: this.YELLOW });
	    this.graph.addEdge("Transform", "Linear", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Transform", "Quadratic", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Transform", "Square Root", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Transform", "Logarithm", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });
	    this.graph.addEdge("Transform", "Differencing", { type: "arrow", label: "activity", size: 3, color: this.YELLOW });

	    this.graph.addEdge("Data Reduction", "Dim.Reduction", { type: "line", label: "subprocess", size: 5 });
	    this.graph.addEdge("Dim.Reduction", "Factor Analysis", { type: "arrow", label: "activity", size: 3 });
	    this.graph.addEdge("Dim.Reduction", "Manually Selected", { type: "arrow", label: "activity", size: 3 });

	    this.graph.addEdge("Behavior", "Trend", { type: "line", label: "subprocess", size: 5 });
	    this.graph.addEdge("Behavior", "Cyclicity", { type: "line", label: "subprocess", size: 5 });
	    this.graph.addEdge("Behavior", "Seasonality", { type: "line", label: "subprocess", size: 5 });

	    // Arrow edges sequences
	    this.graph.addEdge("Cleaning", "Normalization", { type: "arrow", label: "sequence", size: 3 });
	    this.graph.addEdge("Normalization", "Transform", { type: "arrow", label: "sequence", size: 3 });
	    this.graph.addEdge("Transform", "Dim.Reduction", { type: "arrow", label: "sequence", size: 3 });
	    this.graph.addEdge("Dim.Reduction", "Trend", { type: "arrow", label: "sequence", size: 3 });
	    this.graph.addEdge("Trend", "Cyclicity", { type: "arrow", label: "sequence", size: 3 });
	    this.graph.addEdge("Cyclicity", "Seasonality", { type: "arrow", label: "sequence", size: 3 });
	    this.graph.addEdge("Seasonality", "Cleaning", { type: "arrow", label: "sequence", size: 3 });
	    
	    this.graph.nodes().forEach((node, i) => {
		const angle = (i * 2 * Math.PI) / this.graph.order;
		this.graph.setNodeAttribute(node, "x", 100 * Math.cos(angle));
		this.graph.setNodeAttribute(node, "y", 100 * Math.sin(angle));
	    });
	    
	    this.renderer = new Sigma(this.graph, this.container, {
		nodeProgramClasses: {
		    // image: createNodeImageProgram(),
		    gradient: NodeGradientProgram,
		},
		minCameraRatio: 1,
		maxCameraRatio: 10,
		// allowInvalidContainer: true,
		renderEdgeLabels: true
	    });
	    
	    // Create the spring layout and start it
	    this.layout = new ForceLayout(this.graph, { maxIterations: 50 });
	    this.layout.start();

	    setTimeout(() => {this.layout.stop();}, 4000)
	    
	    onStoryDown(() => {
		this.layout.kill();
		this.renderer.kill();
	    });
	}	    
    },
    computed: {
	// end_year: function() {
	//     let res = this.start_year + (this.rangeYear * this.params.points_per_period) / 12
	//     return this.start_year ? Math.round(res) : null
	// }
    },
    mounted: function() {
	this.dataset = this.$route.params.dataset;
	this.station = this.$route.params.station;
	document.getElementById("dynNet").href=`/net/${this.dataset}/${this.station}`;
	document.getElementById("dynVisualize").href=`/visualize/${this.dataset}/${this.station}`;
	document.getElementById("dynStats").href=`/stats/${this.dataset}/${this.station}`;
	document.getElementById("dynSpiral").href=`/spiral/${this.dataset}/${this.station}`;
	console.log("[ Mounted Network View ]: (", this.dataset, ",", this.station, ")");
	this.showNetwork();
    },
    watch: {
	// end_year(newValue) {
	//     console.log("[ WATCH END_YEAR ]", newValue);
	//     this.raw_data = this.orig_data.filter(x => { return x.date > `${this.start_year}-01-01` });
	//     this.renderSpiral();
	//     this.spiral.redraw();
	// }
    }
}
</script>

<style>
img {
    width: 100%;
    height: auto;
}
.labels.segment {
    font: sans-serif;
    font-size: 13px;
    font-family: Arvo;
    font-weight: 300;
}
.custom-step {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    position: relative;
    box-shadow: 0 0 0 3px #ccc;
    background-color: #fff;
    z-index: 3;
}
.custom-step.active {
    box-shadow: 0 0 0 3px #3498db;
    background-color: #3498db;
}
.custom-step-bar.active {
    z-index: 1;
    position: relative;
    margin-top: -25px;
    width: 100%;
    height: 25px;
    border-radius: 25px;
    background-color: rgb(85, 85, 85);
}
table.blockTable {
    writing-mode: horizontal-lr;
    min-width: 50px;
    /* for firefox */
}
.firstRow {
    width: 38vw;
}
td.slideOp:hover {
    background-color: rgba(6, 10, 223, 0.109);
    cursor: pointer;
}
.dataframe tbody tr th:only-of-type {
    vertical-align: middle;
}

.dataframe tbody tr th {
    vertical-align: top;
}

.dataframe thead th {
    text-align: right;
}
</style>
