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
// Available layouts
import ForceLayout from "graphology-layout-force/worker";
// import ForceLayout from "graphology-layout-forceatlas2/worker";
// import ForceLayout from "graphology-layout-noverlap/worker";

import Sigma from "sigma";

import { onStoryDown } from "./utils";
import NodeGradientProgram from "./node-gradient";

import axios from "axios"
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
	LIGHTBLUE: "#3399f8",
	GREEN: "#5DB346",
	YELLOW: "#F6F606",
	GRAY: "#767686",
	BLACK: "#000000",
	PROCSZ: 24,
	SUBPSZ: 18,
	ACTVSZ: 12,
	PROCCO: { // color
            "Data Quality": "#767686",
	    "Data Reduction": "#767686",
            "Variables Behavior": "#767686"
	},
	PROCPR: { // prio
            "Data Quality": 1,
	    "Data Reduction": 2,
            "Variables Behavior": 3
	},
	PROCBY: [], // bypass
	SUBPCO: { // color
	    "Data Quality": {
		"Clean": "#767686",
		"Normalize": "#767686",
		"Transform": "#767686"
	    },
	    "Data Reduction": {
		"DimRed": "#767686"
	    },
	    "Variables Behavior": {
		"Trend": "#767686",
		"Seasonality": "#767686",
		"Cyclicity": "#767686"
	    }
	},
	SUBPPR: { // prio
	    "Data Quality": {
		"Clean": 11,
		"Normalize": 12,
		"Transform": 13
	    },
	    "Data Reduction": {
		"DimRed": 21
	    },
	    "Variables Behavior": {
		"Trend": 31,
		"Seasonality": 32,
		"Cyclicity": 33
	    }
	},
	SUBPBY: [], // bypass
	ACTVCO: { // color
	    "Data Quality": {
		"Clean": {
		    "Rolling Mean": "#767686",
		    "Decision Tree": "#767686",
		    "Stochastic Gradient": "#767686",
		    "Locally Weighted": "#767686",
		    "Legendre": "#767686",
		    "Random Forest": "#767686",
		    "KNN": "#767686"
		},
		"Normalize": {
		    "MinMax": "#767686",
		    "Standard": "#767686",
		    "MaxAbs": "#767686",
		    "Robust": "#767686"
		},
		"Transform": {
		    "Linear": "#767686",
		    "Quadratic": "#767686",
		    "Square Root": "#767686",
		    "Logarithm": "#767686",
		    "Differencing": "#767686"
		}
	    },
	    "Data Reduction": {
		"DimRed": {
		    "Factor Analysis": "#767686",
		    "Manually Selected": "#767686"
		}
	    },
	    "Variables Behavior": {
		"Trend": {
		},
		"Seasonality": {
		},
		"Cyclicity": {
		}
	    }
	},
	ACTVPR: { // prio
	    "Data Quality": {
		"Clean": {
		    "Rolling Mean": 111,
		    "Decision Tree": 112,
		    "Stochastic Gradient": 113,
		    "Locally Weighted": 114,
		    "Legendre": 115,
		    "Random Forest": 116,
		    "KNN": 117
		},
		"Normalize": {
		    "MinMax": 121,
		    "Standard": 122,
		    "MaxAbs": 123,
		    "Robust": 124
		},
		"Transform": {
		    "Linear": 131,
		    "Quadratic": 132,
		    "Square Root": 133,
		    "Logarithm": 134,
		    "Differencing": 135
		}
	    },
	    "Data Reduction": {
		"DimRed": {
		    "Factor Analysis": 211,
		    "Manually Selected": 212
		}
	    },
	    "Variables Behavior": {
		"Trend": {
		},
		"Seasonality": {
		},
		"Cyclicity": {
		}
	    }
	},
	ACTVBY: []
    }),
    methods: {
	async showNetwork() {
	    this.datasetSelected = true;
	    
	    let steprc = await axios.get(
		"http://localhost:8080/recommendation/" + this.dataset + "/" + this.station,
		{ crossdomain: true }
	    );
	    let itrecommends = steprc.data[0];
	    console.log("[ It Recommends ]");
	    // for (var process in itrecommends) {
	    // 	console.log("[ Process ]:", process);
	    // 	console.log("[ Subprocesses ]:", itrecommends[process]);
	    // 	this.PROCCO[process] = this.RED;
	    // 	for (var subprocess in itrecommends[process]) {
	    // 	    this.SUBPCO[process][itrecommends[process][subprocess]] = this.RED;
	    // 	    for (var inactv in this.ACTVCO[process][itrecommends[process][subprocess]]) {
	    // 		this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.RED;
	    // 	    }
	    // 	}
	    // }
	    for (var process in itrecommends) {
		console.log("[ Process ]:", process);
		console.log("[ Subprocesses ]:", itrecommends[process]);
		this.PROCCO[process] = this.RED;
		this.PROCBY.push(this.PROCPR[process]);
		for (var prio_coloring_p in this.PROCPR) {
		    if (! this.PROCBY.includes(this.PROCPR[prio_coloring_p])) {
			if (this.PROCPR[prio_coloring_p] < this.PROCPR[process]) {
			    this.PROCCO[prio_coloring_p] = this.GREEN;
			}
		    }
		}
		for (var subprocess in itrecommends[process]) {
		    this.SUBPCO[process][itrecommends[process][subprocess]] = this.RED;
		    this.SUBPBY.push(this.SUBPPR[process][itrecommends[process][subprocess]]);
		    for (var prio_coloring_s in this.SUBPPR[process]) {
			if (! this.SUBPBY.includes(this.SUBPPR[process][prio_coloring_s])) {
			    if (this.SUBPPR[process][prio_coloring_s] < this.SUBPPR[process][itrecommends[process][subprocess]]) {
				this.SUBPCO[process][prio_coloring_s] = this.GREEN;
				for (var inactv_s_g in this.ACTVCO[process][prio_coloring_s]) {
				    this.ACTVCO[process][prio_coloring_s][inactv_s_g] = this.GREEN;
				}
			    } else {
				this.SUBPCO[process][prio_coloring_s] = this.YELLOW;
				for (var inactv_s_y in this.ACTVCO[process][prio_coloring_s]) {
				    this.ACTVCO[process][prio_coloring_s][inactv_s_y] = this.YELLOW;
				}
			    }
			}
		    }
		    for (var inactv in this.ACTVCO[process][itrecommends[process][subprocess]]) {
			this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.RED;
			this.ACTVBY.push(this.ACTVPR[process][itrecommends[process][subprocess]][inactv]);
		    }
		}
	    }
	    await new Promise(r => setTimeout(r, 2000));
	    this.container = document.getElementById("container");
	    console.log("[ Container ]:", this.container);
	    this.graph = new Graph();
	    
	    // Node processes
	    this.graph.addNode("Data Quality", { size: this.PROCSZ, label: "Data Quality", type: "gradient", color: this.PROCCO["Data Quality"] });
	    this.graph.addNode("Data Reduction", { size: this.PROCSZ, label: "Data Reduction", type: "gradient", color: this.PROCCO["Data Reduction"] });
	    this.graph.addNode("Variables Behavior", { size: this.PROCSZ, label: "Variables Behavior", type: "gradient", color: this.PROCCO["Variables Behavior"] });

	    // Node subprocesses
	    this.graph.addNode("Clean", { size: this.SUBPSZ, label: "Clean", type: "gradient", color: this.SUBPCO["Data Quality"]["Clean"] });
	    this.graph.addNode("Rolling Mean", { size: this.ACTVSZ, label: "Rolling Mean", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["Rolling Mean"] });
	    this.graph.addNode("Decision Tree", { size: this.ACTVSZ, label: "Decision Tree", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["Decision Tree"] });
	    this.graph.addNode("Stochastic Gradient", { size: this.ACTVSZ, label: "Stochastic Gradient", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["Stochastic Gradient"] });
	    this.graph.addNode("Locally Weighted", { size: this.ACTVSZ, label: "Locally Weighted", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["Locally Weighted"] });
	    this.graph.addNode("Legendre", { size: this.ACTVSZ, label: "Legendre", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["Legendre"] });
	    this.graph.addNode("Random Forest", { size: this.ACTVSZ, label: "Random Forest", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["Random Forest"] });
	    this.graph.addNode("KNN", { size: this.ACTVSZ, label: "KNN", type: "gradient", color: this.ACTVCO["Data Quality"]["Clean"]["KNN"] });

	    this.graph.addNode("Normalize", { size: this.SUBPSZ, label: "Normalize", type: "gradient", color: this.SUBPCO["Data Quality"]["Normalize"] });
	    this.graph.addNode("MinMax", { size: this.ACTVSZ, label: "MinMax", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["MinMax"] });
	    this.graph.addNode("Standard", { size: this.ACTVSZ, label: "Standard", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["Standard"] });
	    this.graph.addNode("MaxAbs", { size: this.ACTVSZ, label: "MaxAbs", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["MaxAbs"] });
	    this.graph.addNode("Robust", { size: this.ACTVSZ, label: "Robust", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["Robust"] });

	    this.graph.addNode("Transform", { size: this.SUBPSZ, label: "Transform", type: "gradient", color: this.SUBPCO["Data Quality"]["Transform"] });
	    this.graph.addNode("Linear", { size: this.ACTVSZ, label: "Linear", type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Linear"] });
	    this.graph.addNode("Quadratic", { size: this.ACTVSZ, label: "Quadratic", type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Quadratic"] });
	    this.graph.addNode("Square Root", { size: this.ACTVSZ, label: "Square Root", type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Square Root"] });
	    this.graph.addNode("Logarithm", { size: this.ACTVSZ, label: "Logarithm", type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Logarithm"] });
	    this.graph.addNode("Differencing", { size: this.ACTVSZ, label: "Differencing", type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Differencing"] });

	    this.graph.addNode("DimRed", { size: this.SUBPSZ, label: "DimRed", type: "gradient", color: this.SUBPCO["Data Reduction"]["DimRed"] });
	    this.graph.addNode("Factor Analysis", { size: this.ACTVSZ, label: "Factor Analysis", type: "gradient", color: this.ACTVCO["Data Reduction"]["DimRed"]["Factor Analysis"] });
	    this.graph.addNode("Manually Selected", { size: this.ACTVSZ, label: "Manually Selected", type: "gradient", color: this.ACTVCO["Data Reduction"]["DimRed"]["Manually Selected"] });

	    this.graph.addNode("Trend", { size: this.SUBPSZ, label: "Trend", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Trend"] });

	    this.graph.addNode("Cyclicity", { size: this.SUBPSZ, label: "Cyclicity", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Cyclicity"] });

	    this.graph.addNode("Seasonality", { size: this.SUBPSZ, label: "Seasonality", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Seasonality"] });
	    
	    // Edge processes
	    this.graph.addEdge("Data Quality", "Data Reduction", { type: "line", label: "process", size: 7, color: this.GREEN });
	    this.graph.addEdge("Data Reduction", "Variables Behavior", { type: "line", label: "process", size: 7, color: this.GREEN });
	    this.graph.addEdge("Data Quality", "Variables Behavior", { type: "line", label: "process", size: 7, color: this.GREEN });

	    // Edge subprocesses
	    this.graph.addEdge("Data Quality", "Clean", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Data Quality"]["Clean"] });
	    this.graph.addEdge("Clean", "Rolling Mean", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["Rolling Mean"] });
	    this.graph.addEdge("Clean", "Decision Tree", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["Decision Tree"] });
	    this.graph.addEdge("Clean", "Stochastic Gradient", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["Stochastic Gradient"] });
	    this.graph.addEdge("Clean", "Locally Weighted", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["Locally Weighted"] });
	    this.graph.addEdge("Clean", "Legendre", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["Legendre"] });
	    this.graph.addEdge("Clean", "Random Forest", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["Random Forest"] });
	    this.graph.addEdge("Clean", "KNN", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Clean"]["KNN"] });

	    this.graph.addEdge("Data Quality", "Normalize", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Data Quality"]["Normalize"] });
	    this.graph.addEdge("Normalize", "MinMax", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["MinMax"] });
	    this.graph.addEdge("Normalize", "Standard", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["Standard"] });
	    this.graph.addEdge("Normalize", "MaxAbs", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["MaxAbs"] });
	    this.graph.addEdge("Normalize", "Robust", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["Robust"] });
	    
	    this.graph.addEdge("Data Quality", "Transform", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Data Quality"]["Transform"] });
	    this.graph.addEdge("Transform", "Linear", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Linear"] });
	    this.graph.addEdge("Transform", "Quadratic", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Quadratic"] });
	    this.graph.addEdge("Transform", "Square Root", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Square Root"] });
	    this.graph.addEdge("Transform", "Logarithm", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Logarithm"] });
	    this.graph.addEdge("Transform", "Differencing", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Differencing"] });

	    this.graph.addEdge("Data Reduction", "DimRed", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Data Reduction"]["DimRed"] });
	    this.graph.addEdge("DimRed", "Factor Analysis", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Reduction"]["DimRed"]["Factor Analysis"] });
	    this.graph.addEdge("DimRed", "Manually Selected", { type: "arrow", label: "activity", size: 3, color: this.ACTVCO["Data Reduction"]["DimRed"]["Manually Selected"] });

	    this.graph.addEdge("Variables Behavior", "Trend", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Variables Behavior"]["Trend"] });

	    this.graph.addEdge("Variables Behavior", "Cyclicity", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Variables Behavior"]["Cyclicity"] });

	    this.graph.addEdge("Variables Behavior", "Seasonality", { type: "arrow", label: "subprocess", size: 5, color: this.SUBPCO["Variables Behavior"]["Seasonality"] });

	    // Edge sequences
	    this.graph.addEdge("Clean", "Normalize", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    this.graph.addEdge("Normalize", "Transform", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    this.graph.addEdge("Transform", "DimRed", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    this.graph.addEdge("DimRed", "Trend", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    this.graph.addEdge("Trend", "Cyclicity", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    this.graph.addEdge("Cyclicity", "Seasonality", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    this.graph.addEdge("Seasonality", "Clean", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    
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

	    setTimeout(() => {this.layout.stop();}, 4000);
	    
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
