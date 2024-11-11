<template>
<v-container class="my-6" fluid>
  <div class="text-center load-layer" v-if="loading_data">
    <v-progress-circular :size="100" class="loader" color="primary" indeterminate>
      Loading data...
    </v-progress-circular>
  </div>
  <div class="text-center load-layer" v-if="executing_task">
    <v-progress-circular :size="100" class="loader" color="primary" indeterminate>
      Executing Task...
    </v-progress-circular>
  </div>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <h2>Dataset: {{ dataset.toUpperCase() }}, Station: {{ station.toUpperCase() }}</h2>
  </v-row>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <v-col cols="10">
      <div v-html="rawcontainer"></div>
    </v-col>
  </v-row>
  <v-dialog v-model="dialog" width="500">
    <v-card mt="4">
      <v-card-title class="headline grey lighten-2">
        Microtask Parameter
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="parameters_form">
            <v-row align="center" justify="center">
              <v-col>
                <v-text-field label="List of features (comma-separated)" v-model="n_comp" ref="n_comp"
			      v-if="main_operation === 'reduce'" :rules="[v => !!v || 'At least one feature to drop']" />
                <v-text-field label="Transform factor" v-model="factor" ref="factor"
			      v-if="main_operation === 'transform'" :rules="[v => !!v || 'Required']" />
                <!-- <v-select label="Feature" v-model="feature" -->
		<!-- 	  :items="[ -->
		<!-- 		  { text: 'Precipitation', value: 0 }, -->
		<!-- 		  { text: 'Temp Max', value: 1 }, -->
		<!-- 		  { text: 'Temp Min', value: 2 } -->
		<!-- 		  ]" -->
		<!-- 	  ref="feature" v-if="main_operation === 'trend' || -->
		<!-- 			      main_operation === 'seasonality' || -->
		<!-- 			      main_operation === 'cyclicity'" -->
		<!-- 	  :rules="[v => !!v || 'Required']" /> -->
              </v-col>
              <v-col>
                <v-btn @click="execActivityParams" large color="primary">
                  Apply</v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
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
	loading_data: true,
	executing_task: false,
	dialog: false,
	n_comp: "",
	factor: 1,
	main_operation: "",
	main_path: "",
	RED: "#FA4F40", // ACTION Enabler
	ORANGE: "#FF6600", // ACTION Enabler
	BLUE: "#727EE0", // ACTION Enabler
	LIGHTBLUE: "#3399f8",
	GREEN: "#5DB346",
	YELLOW: "#F6F606",
	GRAY: "#767686",
	BLACK: "#000000",
	PROCSZ: 24, // Process
	SUBPSZ: 18, // Subprocess
	ACTVSZ: 12, // Activity in ACTION
	PROCCO: { // Default color GRAY
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
	SUBPCO: { // Default color GRAY
	    "Data Quality": {
		"Clean": "#767686",
		"Nulls": "#767686",
		"Outliers": "#767686",
		"Normalize": "#767686",
		"Transform": "#767686"
	    },
	    "Data Reduction": {
		"DimRed": "#767686"
	    },
	    // "Variables Behavior": {
	    // 	"Trend": "#767686",
	    // 	"Seasonality": "#767686",
	    // 	"Cyclicity": "#767686"
	    // }
	    "Variables Behavior": {
		"Analysis": "#767686"
	    }
	},
	SUBPPR: { // prio
	    "Data Quality": {
		"Clean": 11,
		"Nulls": 12,
		"Outliers": 13,
		"Normalize": 14,
		"Transform": 15
	    },
	    "Data Reduction": {
		"DimRed": 21
	    },
	    // "Variables Behavior": {
	    // 	"Trend": 31,
	    // 	"Seasonality": 32,
	    // 	"Cyclicity": 33
	    // }
	    "Variables Behavior": {
		"Analysis": 31
	    }
	},
	SUBPBY: [], // bypass
	ACTVCO: { // Default color GRAY
	    "Data Quality": {
		"Clean": {
		},
		"Nulls": {
		    "Rolling Mean": "#767686",
		    "Decision Tree": "#767686",
		    "Stochastic Gradient": "#767686",
		    "Locally Weighted": "#767686",
		    "Legendre": "#767686",
		    "Random Forest": "#767686",
		    "KNN": "#767686"
		},
		"Outliers": {
		    "Interquartile Range": "#767686",
		    "Z-Score": "#767686"
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
	    // "Variables Behavior": {
	    // 	"Trend": {
	    // 	},
	    // 	"Seasonality": {
	    // 	},
	    // 	"Cyclicity": {
	    // 	}
	    // }
	    "Variables Behavior": {
		"Analysis": {
		    "Trend": "#767686",
		    "Seasonality": "#767686",
		    "Cyclicity": "#767686"
		}
	    }
	},
	ACTVPR: { // prio
	    "Data Quality": {
		"Clean": {
		},
		"Nulls": {
		    "Rolling Mean": 121,
		    "Decision Tree": 122,
		    "Stochastic Gradient": 123,
		    "Locally Weighted": 124,
		    "Legendre": 125,
		    "Random Forest": 126,
		    "KNN": 127
		},
		"Outliers": {
		    "Interquartile Range": 131,
		    "Z-Score": 132
		},
		"Normalize": {
		    "MinMax": 141,
		    "Standard": 142,
		    "MaxAbs": 143,
		    "Robust": 144
		},
		"Transform": {
		    "Linear": 151,
		    "Quadratic": 152,
		    "Square Root": 153,
		    "Logarithm": 154,
		    "Differencing": 155
		}
	    },
	    "Data Reduction": {
		"DimRed": {
		    "Factor Analysis": 211,
		    "Manually Selected": 212
		}
	    },
	    // "Variables Behavior": {
	    // 	"Trend": {
	    // 	},
	    // 	"Seasonality": {
	    // 	},
	    // 	"Cyclicity": {
	    // 	}
	    // }
	    "Variables Behavior": {
		"Analysis": {
		    "Trend": 311,
		    "Seasonality": 312,
		    "Cyclicity": 313
		}
	    }
	},
	ACTVBY: []
    }),
    methods: {
	async execActivity(event, itemType, item) {
	    if (event === "clickNode") {
		let label;
		let color;
		let size;
		let path;
		let action = false;
		if (item && itemType) {
		    if (itemType === "node") {
			label = this.graph.getNodeAttribute(item, "label");
			color = this.graph.getNodeAttribute(item, "color");
			size = this.graph.getNodeAttribute(item, "size");
			path = this.graph.getNodeAttribute(item, "path");
			if (label == "Linear" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    this.main_operation = "transform";
			    this.main_path = "transform/linear/";
			    this.dialog = true;
			} else if (label == "Manually Selected" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    this.main_operation = "reduce";
			    this.main_path = "reduce/manual/";
			    this.dialog = true;
			} else if ((color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    action = true;
			}
			console.log("[", event, "]:", itemType, label, "action:", action);
		    } else if (itemType === "edge") {
			label = this.graph.getEdgeAttribute(item, "label");
			console.log("[", event, "]:", itemType, label);
		    } else {
			console.log("[", event, "]:", itemType, "unhandled");
		    }
		}
		if (action) {
		    if (path.startsWith("/")) {
			location.href = `${path}/${this.dataset}/${this.station}`;
		    } else {
			this.executing_task = true;
			let req_string;
			req_string = `http://localhost:8080/op/${this.dataset}/${path}`;
			// this.history.push({
			// 	name: `${this.operation.method}-clean`,
			// 	aux: req_string
			// })
			console.log(req_string);
			let actionrc = await axios.get(req_string, { crossdomain: true });
			console.log(actionrc);
			this.executing_task = false;
			location.reload();
		    }
		}
	    } else {	
		console.log("[", event, "]:", "unhandled");
	    }
	},
	async execActivityParams() {
	    console.log("[ Action with params ]");
	    if (this.main_operation === "reduce" && this.n_comp === "") {
		this.$refs["n_comp"].validate(true);
		return;
	    }
	    if (this.main_operation === "transform" && this.factor === "") {
		this.$refs["factor"].validate(true);
		return;
	    }
	    if (this.main_operation === "reduce") this.main_path = this.main_path + this.n_comp;
	    if (this.main_operation === "transform") this.main_path = this.main_path + this.factor;
	    this.executing_task = true;
	    let req_string;
	    req_string = `http://localhost:8080/op/${this.dataset}/${this.main_path}`;
	    console.log(req_string);
	    let actionrc = await axios.get(req_string, { crossdomain: true });
	    console.log(actionrc);
	    this.executing_task = false;
	    this.dialog = false;
	    this.$refs["parameters_form"].reset();
	    location.reload();
	},
	async showNetwork() {
	    this.datasetSelected = true;
	    let steprc = await axios.get(
		"http://localhost:8080/recommendation/" + this.dataset + "/" + this.station,
		{ crossdomain: true }
	    );
	    let itrecommends = steprc.data[0];
	    let itextends = steprc.data[1];
	    console.log("[ It Recommends ]");
	    for (var process in itrecommends) {
		// if (process != "Excluded Activities") {
		console.log("[ Process ]:", process);
		console.log("[ Subprocesses ]:", itrecommends[process]);
		console.log("[ Subprocess Excluded Activities ]:", itextends["Excluded Activities"]);
		this.PROCCO[process] = this.PROCPR[process] == 3 ? this.BLUE : this.RED;
		this.PROCBY.push(this.PROCPR[process]);
		for (var prio_coloring_p in this.PROCPR) {
		    if (! this.PROCBY.includes(this.PROCPR[prio_coloring_p])) {
			if (this.PROCPR[prio_coloring_p] < this.PROCPR[process]) {
			    this.PROCCO[prio_coloring_p] = this.GREEN;
			    for (var prio_coloring_a in this.SUBPCO[prio_coloring_p]) {
				this.SUBPCO[prio_coloring_p][prio_coloring_a] = this.GREEN;
				for (var prio_coloring_b in this.ACTVCO[prio_coloring_p][prio_coloring_a]) {
				    this.ACTVCO[prio_coloring_p][prio_coloring_a][prio_coloring_b] = this.GREEN;
				}
			    }
			}
		    }
		}
		for (var subprocess in itrecommends[process]) {
		    // this.SUBPCO[process][itrecommends[process][subprocess]] = this.SUBPPR[process][itrecommends[process][subprocess]] > 30 ? this.BLUE : this.RED;
		    if ( this.SUBPPR[process][itrecommends[process][subprocess]] > 30 ) {
			this.SUBPCO[process][itrecommends[process][subprocess]] = this.BLUE;
		    } else if ( this.SUBPPR[process][itrecommends[process][subprocess]] == 15 ) {
			this.SUBPCO[process][itrecommends[process][subprocess]] = this.ORANGE;
			if ( itrecommends[process].length == 1 ) {
			    this.PROCCO[process] = this.ORANGE;
			}
		    } else {
			this.SUBPCO[process][itrecommends[process][subprocess]] = this.RED;
		    }
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
		    console.log("[ Activities ]:");
		    for (var inactv in this.ACTVCO[process][itrecommends[process][subprocess]]) {
			console.log(" ", inactv);
			// if (typeof itextends["Excluded Activities"] !== "undefined" &&
			//     itextends["Excluded Activities"].includes(inactv)) {
			//     this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.GREEN;
			// } else {
			//     this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.RED;
			//     this.ACTVBY.push(this.ACTVPR[process][itrecommends[process][subprocess]][inactv]);
			// }
			if (typeof itextends["Excluded Activities"] !== "undefined" && itextends["Excluded Activities"].length > 0) {
			    if (itextends["Excluded Activities"].includes(inactv)) {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.GREEN;
			    } else {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.ACTVPR[process][itrecommends[process][subprocess]][inactv] > 300 ? this.BLUE : this.ORANGE;
				this.ACTVBY.push(this.ACTVPR[process][itrecommends[process][subprocess]][inactv]);
			    }
			} else {
			    // this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.ACTVPR[process][itrecommends[process][subprocess]][inactv] > 300 ? this.BLUE : this.RED;
			    if ( this.ACTVPR[process][itrecommends[process][subprocess]][inactv] > 300 ) {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.BLUE;
			    } else if ( this.ACTVPR[process][itrecommends[process][subprocess]][inactv] % 150 < 10 ) {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.ORANGE;
			    } else {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.RED;
			    }
			    this.ACTVBY.push(this.ACTVPR[process][itrecommends[process][subprocess]][inactv]);
			}
		    }
		}
		// }
	    }
	    if (typeof itextends["DimRed"] !== "undefined") {
		console.log(itextends["DimRed"]);
		const foundFA = itextends["DimRed"].find(item => item.includes("FA Dim.Reduction"));
		if (foundFA) {
		    const regex = /\[(.*?)\]/;
		    const matchFA = foundFA.match(regex);
		    if (matchFA) {
			const valuesFA = matchFA[1].split(',').map(item => item.trim().replace(/'/g, ''));
			console.log(valuesFA);
			this.n_comp = valuesFA.join(',');
			console.log(this.n_comp);
		    }
		}
		if (this.n_comp == "") {
		    const foundMC = itextends["DimRed"].find(item => item.includes("Multicollinearity Dim.Reduction"));
		    if (foundMC) {
			const regex = /\[(.*?)\]/;
			const matchMC = foundMC.match(regex);
			if (matchMC) {
			    const valuesMC = matchMC[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesMC);
			    this.n_comp = valuesMC.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
		if (this.n_comp == "") {
		    const foundPR = itextends["DimRed"].find(item => item.includes("Pearson Dim.Reduction"));
		    if (foundPR) {
			const regex = /\[(.*?)\]/;
			const matchPR = foundPR.match(regex);
			if (matchPR) {
			    const valuesPR = matchPR[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesPR);
			    this.n_comp = valuesPR.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
		if (this.n_comp == "") {
		    const foundSP = itextends["DimRed"].find(item => item.includes("Spearman Dim.Reduction"));
		    if (foundSP) {
			const regex = /\[(.*?)\]/;
			const matchSP = foundSP.match(regex);
			if (matchSP) {
			    const valuesSP = matchSP[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesSP);
			    this.n_comp = valuesSP.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
		if (this.n_comp == "") {
		    const foundKN = itextends["DimRed"].find(item => item.includes("Kendall Dim.Reduction"));
		    if (foundKN) {
			const regex = /\[(.*?)\]/;
			const matchKN = foundKN.match(regex);
			if (matchKN) {
			    const valuesKN = matchKN[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesKN);
			    this.n_comp = valuesKN.join(',');
			    console.log(this.n_comp);
			}
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
	    this.graph.addNode("Clean", { size: this.SUBPSZ, label: "Cleanning", type: "gradient", color: this.SUBPCO["Data Quality"]["Clean"] });
	    
	    this.graph.addNode("Nulls", { size: this.SUBPSZ, label: "Nulls", type: "gradient", color: this.SUBPCO["Data Quality"]["Nulls"] });
	    this.graph.addNode("Rolling Mean", { size: this.ACTVSZ, label: "Rolling Mean", path: "clean/rm", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Rolling Mean"] });
	    this.graph.addNode("Decision Tree", { size: this.ACTVSZ, label: "Decision Tree", path: "clean/dtr", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Decision Tree"] });
	    this.graph.addNode("Stochastic Gradient", { size: this.ACTVSZ, label: "Stochastic Gradient", path: "clean/sgb", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Stochastic Gradient"] });
	    this.graph.addNode("Locally Weighted", { size: this.ACTVSZ, label: "Locally Weighted", path: "clean/lwr", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Locally Weighted"] });
	    this.graph.addNode("Legendre", { size: this.ACTVSZ, label: "Legendre", path: "clean/lgd", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Legendre"] });
	    this.graph.addNode("Random Forest", { size: this.ACTVSZ, label: "Random Forest", path: "clean/rfr", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Random Forest"] });
	    this.graph.addNode("KNN", { size: this.ACTVSZ, label: "KNN", path: "clean/knn", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["KNN"] });
	    
	    this.graph.addNode("Outliers", { size: this.SUBPSZ, label: "Outliers", type: "gradient", color: this.SUBPCO["Data Quality"]["Outliers"] });
	    this.graph.addNode("Interquartile Range", { size: this.ACTVSZ, label: "Interquartile Range", path: "outliers/iqr", type: "gradient", color: this.ACTVCO["Data Quality"]["Outliers"]["Interquartile Range"] });
	    this.graph.addNode("Z-Score", { size: this.ACTVSZ, label: "Z-Score", path: "outliers/sdv", type: "gradient", color: this.ACTVCO["Data Quality"]["Outliers"]["Z-Score"] });
	    
	    this.graph.addNode("Normalize", { size: this.SUBPSZ, label: "Normalization", type: "gradient", color: this.SUBPCO["Data Quality"]["Normalize"] });
	    this.graph.addNode("MinMax", { size: this.ACTVSZ, label: "MinMax", path: "normalize/minmax", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["MinMax"] });
	    this.graph.addNode("Standard", { size: this.ACTVSZ, label: "Standard", path: "normalize/standard", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["Standard"] });
	    this.graph.addNode("MaxAbs", { size: this.ACTVSZ, label: "MaxAbs", path: "normalize/maxabs", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["MaxAbs"] });
	    this.graph.addNode("Robust", { size: this.ACTVSZ, label: "Robust", path: "normalize/robust", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["Robust"] });
	    
	    this.graph.addNode("Transform", { size: this.SUBPSZ, label: "Transformation", type: "gradient", color: this.SUBPCO["Data Quality"]["Transform"] });
	    this.graph.addNode("Linear", { size: this.ACTVSZ, label: "Linear", path: "transform/linear/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Linear"] });
	    this.graph.addNode("Quadratic", { size: this.ACTVSZ, label: "Quadratic", path: "transform/quadratic/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Quadratic"] });
	    this.graph.addNode("Square Root", { size: this.ACTVSZ, label: "Square Root", path: "transform/sqrt/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Square Root"] });
	    this.graph.addNode("Logarithm", { size: this.ACTVSZ, label: "Logarithm", path: "transform/log/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Logarithm"] });
	    this.graph.addNode("Differencing", { size: this.ACTVSZ, label: "Differencing", path: "transform/diff/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Differencing"] });
	    
	    this.graph.addNode("DimRed", { size: this.SUBPSZ, label: "Dim. Reduction", type: "gradient", color: this.SUBPCO["Data Reduction"]["DimRed"] });
	    this.graph.addNode("Factor Analysis", { size: this.ACTVSZ, label: "Factor Analysis", path: "reduce/factor/" + this.n_comp, type: "gradient", color: this.ACTVCO["Data Reduction"]["DimRed"]["Factor Analysis"] });
	    this.graph.addNode("Manually Selected", { size: this.ACTVSZ, label: "Manually Selected", path: "reduce/manual/" + this.n_comp, type: "gradient", color: this.ACTVCO["Data Reduction"]["DimRed"]["Manually Selected"] });
	    
	    // this.graph.addNode("Trend", { size: this.SUBPSZ, label: "Trend", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Trend"] });
	    
	    // this.graph.addNode("Cyclicity", { size: this.SUBPSZ, label: "Cyclicity", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Cyclicity"] });
	    
	    // this.graph.addNode("Seasonality", { size: this.SUBPSZ, label: "Seasonality", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Seasonality"] });

	    this.graph.addNode("Analysis", { size: this.SUBPSZ, label: "Analysis", type: "gradient", color: this.SUBPCO["Variables Behavior"]["Analysis"] });
	    this.graph.addNode("Trend", { size: this.ACTVSZ, label: "Trend", path: "", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Trend"] });
	    this.graph.addNode("Cyclicity", { size: this.ACTVSZ, label: "Cyclicity", path: "/spiral", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Cyclicity"] });
	    this.graph.addNode("Seasonality", { size: this.ACTVSZ, label: "Seasonality", path: "", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Seasonality"] });
	    
	    // Edge processes
	    this.graph.addEdge("Data Quality", "Data Reduction", { type: "arrow", label: "macrotarea", size: 7, color: this.GREEN });
	    this.graph.addEdge("Data Reduction", "Variables Behavior", { type: "arrow", label: "macrotarea", size: 7, color: this.GREEN });
	    // this.graph.addEdge("Data Quality", "Variables Behavior", { type: "arrow", label: "macrotarea", size: 7, color: this.GREEN });
	    
	    // Edge subprocesses
	    this.graph.addEdge("Data Quality", "Clean", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Data Quality"]["Clean"] });
	    
	    this.graph.addEdge("Clean", "Nulls", { type: "arrow", label: "subtarea", size: 5, color: this.SUBPCO["Data Quality"]["Nulls"] });
	    this.graph.addEdge("Nulls", "Rolling Mean", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Rolling Mean"] });
	    this.graph.addEdge("Nulls", "Decision Tree", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Decision Tree"] });
	    this.graph.addEdge("Nulls", "Stochastic Gradient", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Stochastic Gradient"] });
	    this.graph.addEdge("Nulls", "Locally Weighted", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Locally Weighted"] });
	    this.graph.addEdge("Nulls", "Legendre", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Legendre"] });
	    this.graph.addEdge("Nulls", "Random Forest", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Random Forest"] });
	    this.graph.addEdge("Nulls", "KNN", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["KNN"] });
	    
	    this.graph.addEdge("Clean", "Outliers", { type: "arrow", label: "subtarea", size: 5, color: this.SUBPCO["Data Quality"]["Outliers"] });
	    this.graph.addEdge("Outliers", "Interquartile Range", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Outliers"]["Interquartile Range"] });
	    this.graph.addEdge("Outliers", "Z-Score", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Outliers"]["Z-Score"] });
	    
	    this.graph.addEdge("Data Quality", "Normalize", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Data Quality"]["Normalize"] });
	    this.graph.addEdge("Normalize", "MinMax", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["MinMax"] });
	    this.graph.addEdge("Normalize", "Standard", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["Standard"] });
	    this.graph.addEdge("Normalize", "MaxAbs", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["MaxAbs"] });
	    this.graph.addEdge("Normalize", "Robust", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["Robust"] });
	    
	    this.graph.addEdge("Data Quality", "Transform", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Data Quality"]["Transform"] });
	    this.graph.addEdge("Transform", "Linear", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Linear"] });
	    this.graph.addEdge("Transform", "Quadratic", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Quadratic"] });
	    this.graph.addEdge("Transform", "Square Root", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Square Root"] });
	    this.graph.addEdge("Transform", "Logarithm", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Logarithm"] });
	    this.graph.addEdge("Transform", "Differencing", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Differencing"] });
	    
	    this.graph.addEdge("Data Reduction", "DimRed", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Data Reduction"]["DimRed"] });
	    this.graph.addEdge("DimRed", "Factor Analysis", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Reduction"]["DimRed"]["Factor Analysis"] });
	    this.graph.addEdge("DimRed", "Manually Selected", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Data Reduction"]["DimRed"]["Manually Selected"] });
	    
	    // this.graph.addEdge("Variables Behavior", "Trend", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Variables Behavior"]["Trend"] });
	    
	    // this.graph.addEdge("Variables Behavior", "Cyclicity", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Variables Behavior"]["Cyclicity"] });
	    
	    // this.graph.addEdge("Variables Behavior", "Seasonality", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Variables Behavior"]["Seasonality"] });

	    this.graph.addEdge("Variables Behavior", "Analysis", { type: "arrow", label: "tarea", size: 5, color: this.SUBPCO["Variables Behavior"]["Analysis"] });
	    this.graph.addEdge("Analysis", "Trend", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Trend"] });
	    this.graph.addEdge("Analysis", "Cyclicity", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Cyclicity"] });
	    this.graph.addEdge("Analysis", "Seasonality", { type: "arrow", label: "microtarea", size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Seasonality"] });
	    
	    // Edge sequences
	    // this.graph.addEdge("Clean", "Normalize", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Normalize", "Transform", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Transform", "DimRed", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("DimRed", "Trend", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Trend", "Cyclicity", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Cyclicity", "Seasonality", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Seasonality", "Clean", { type: "arrow", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    
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
	    this.loading_data = false
	    this.layout.start();
	    
	    setTimeout(() => {this.layout.stop();}, 4000);
	    
	    // const nodeEvents = [
	    // 	"enterNode",
	    // 	"leaveNode",
	    // 	"downNode",
	    // 	"clickNode",
	    // 	"rightClickNode",
	    // 	"doubleClickNode",
	    // 	"wheelNode",
	    // ] as const;
	    // nodeEvents.forEach((eventType) => this.renderer.on(eventType, ({ node }) => this.logEvent(eventType, "node", node)));
	    this.renderer.on("clickNode", ({ node }) => this.execActivity("clickNode", "node", node));
	    
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
	axios.get(
	    "http://localhost:8080/data/" + this.dataset + "/" + this.station,
	    { crossdomain: true }
	).then(async meta => {
	    console.log("[ Mounted Raw Data Length ]:", meta.data.length)
	});
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
</style>
