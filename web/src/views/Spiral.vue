<template>
<v-container class="my-6" fluid>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <h2>Dataset: {{ dataset.toUpperCase() }}, Station: {{ station.toUpperCase() }}</h2>
    <v-col cols="12" class="text-center">
      <span>
	Max Value for Range is 10 due to visualization size reasons.
      </span>
    </v-col>
    <v-col cols="2">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
    </v-col>
    <v-col cols="3">
      <v-select v-model="feature" :items="featureitems" item-text="text" item-value="value" label="Feature" placeholder="Select a feature" outlined />
    </v-col>
    <v-col cols="3">
      <v-select v-model="start_year" :items="year_items" item-text="text" item-value="value" label="Start year" placeholder="Select a year" outlined />
    </v-col>
    <v-col cols="3">
      <v-text-field v-model="end_year" label="End year" placeholder="Select a year" outlined readonly />
    </v-col>
  </v-row>
  <v-row dense class="text-center text-h6" v-if="datasetSelected">
    <v-col>
      Selected date: {{ selectedDate }} - Value: {{ selectedValue }}
      <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
          <v-icon color="primary" dark v-bind="attrs" v-on="on">
            mdi-help-circle-outline
          </v-icon>
        </template>
        <span>
          Here you can find the value of the segment selected, above you can
          find a legend for the values shown on the spiral and next to them, a
          serie of <b>Star Glyphs</b>, each of them shows the
          <b>multivariate</b> information of the time series in a certain
          time.
        </span>
      </v-tooltip>
    </v-col>
  </v-row>
  <v-row class="text-center" v-if="datasetSelected">
    <v-col cols="2">
      <v-navigation-drawer v-model="drawer" absolute width="20%">
        <v-list nav dense>
          <v-list-item>
            <v-list-item-content>
              <v-row justify="center">
                <v-col cols="12">
                  <v-list-item-title>
                    <div class="text-h6">
                      Segs. per cycle: {{ params.points_per_period }}
                      <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon color="primary" dark v-bind="attrs" v-on="on">
                            mdi-help-circle-outline
                          </v-icon>
                        </template>
                        <span> Number of Radial Segments in the Spiral </span>
                      </v-tooltip>
                    </div>
                  </v-list-item-title>
                </v-col>
                <v-col cols="11">
                  <vue-slider v-model="params.points_per_period" :min="2" :max="periodsMax" :step="1" marks hide-label>
                    <template v-slot:step="{ label }">
                      <div :class="[ 'custom-step-bar', guide_cycle.includes(label) ? 'active' : '' ]"></div>
                    </template>
                  </vue-slider>
                </v-col>
              </v-row>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <v-row justify="center">
                <v-col cols="12">
                  <v-list-item-title>
		    <div class="text-h6">
                      # Cycles: {{ rangeYear }}
                      <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon color="primary" dark v-bind="attrs" v-on="on">
                            mdi-help-circle-outline
                          </v-icon>
                        </template>
                        <span> Number of Cycles in the Spiral </span>
                      </v-tooltip>
                    </div>
                  </v-list-item-title>
                </v-col>
                <v-col cols="11">
                  <vue-slider v-model="rangeYear" :min="1" :max="cyclesMax">
                  </vue-slider>
                </v-col>
              </v-row>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <v-row justify="center">
                <v-col cols="12">
                  <v-list-item-title>
		    <div class="text-h6">
                      Spiral Radius: {{ params.radius }}
                      <v-tooltip top>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon color="primary" dark v-bind="attrs" v-on="on">
                            mdi-help-circle-outline
                          </v-icon>
                        </template>
                        <span> Spiral's Radius </span>
                      </v-tooltip>
                    </div>
                  </v-list-item-title>
                </v-col>
                <v-col cols="11">
                  <vue-slider v-model="params.radius" :min="10" :max="100">
                  </vue-slider>
                </v-col>
              </v-row>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>
    </v-col>
    <v-col>
      <div id="chart-legend"></div>
      <div id="chart"></div>
    </v-col>
    <v-col class="text-center">
      <v-row class="text-center">
	<v-col v-for="(feat, fidx) in features" v-bind:key="fidx">
	  <div :class="ftcolors[fidx%16]">
            <span class="white--text">
	      {{ feat }}
              <v-tooltip top>
                <template v-slot:activator="{ on, attrs }">
                  <v-icon color="white" dark v-bind="attrs" v-on="on">
                    mdi-help-circle-outline
                  </v-icon>
                </template>
                <span>
		  Feature: {{ feat }}, Index: {{ fidx }}
                </span>
              </v-tooltip>
            </span>
          </div>
	</v-col>
      </v-row>
      <v-row class="text-center mb-8">
        <v-col v-for="(info, key) in variation_info" v-bind:key="key">
          <div class="text-center rounded">
            <span class="font-weight-bold">σ: {{ info }}</span>
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col
          v-for="(year_lines, index) in year_cycle_data"
          v-bind:key="index"
          :cols="rangeYear > 5 ? '4' : '6'">
          {{ year_info[index] }} |
          <svg width="100%" height="200"
	       :viewBox="`-${viewBoxSize / 2} -${viewBoxSize / 2} ${viewBoxSize} ${viewBoxSize}`"
	       xmlns="http://www.w3.org/2000/svg">
            <g>
              <polygon :points="getPolygonCoords(index)" fill="gray" fill-opacity="0.3" stroke="gray" stroke-width="0.5" />
	      <line x1="0" y1="0" :x2="year_lines[0].x" :y2="year_lines[0].y" :stroke="skcolors[0]" stroke-width="0.5" />
              <line x1="0" y1="0" :x2="year_lines[1].x" :y2="year_lines[1].y" :stroke="skcolors[1]" stroke-width="0.5" />
              <line x1="0" y1="0" :x2="year_lines[2].x" :y2="year_lines[2].y" :stroke="skcolors[2]" stroke-width="0.5" />
            </g>
          </svg>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</v-container>
</template>

<script>
// -*- mode: JavaScript -*-
import { AppBus } from '../appBus';
import Spiral from "@/views/point_spiral"
import * as d3 from "d3"
import axios from "axios"
import VueSlider from "vue-slider-component"
import "vue-slider-component/theme/default.css"
export default {
    name: "Spiral",
    components: {
	VueSlider
    },
    data: () => ({
	params: {
	    rotation: 0,
	    radius: 20,
	    points_per_period: 12,
	    cycles: 5
	},
	periodsBase: 36,
	periodsMax: 36,
	cyclesMax: 15,
	initialState: true,
	dataset: "majes",
	station: "majes",
	drawer: true,
	items: [
	    { text: "MAJES", value: "majes" },
	    { text: "CHIGUATA", value: "chiguata" },
	    { text: "JOYA", value: "joya" },
	    { text: "PAMPILLA", value: "pampilla" }
	],
	datasetSelected: false,
	x: d3
	    .scaleLinear()
	    .range([-100, 100])
	    .domain([-750, 750]),
	y: d3
	    .scaleLinear()
	    .range([-100, 100])
	    .domain([-500, 500]),
	lines: [
	    { x: 1, y: 1 },
	    { x: 1, y: 1 },
	    { x: 1, y: 1 }
	],
	featureitems: [
	    { text: "Precipitation", value: "precipitation" },
	    { text: "Temp Max", value: "tempMax" },
	    { text: "Temp Min", value: "tempMin" }
	],
	// features: [ "precipitation", "tempMax", "tempMin" ],
	features: [],
	ftcolors: [
	    "blue darken-2 text-center rounded",
	    "green darken-2 text-center rounded",
	    "red darken-2 text-center rounded",
	    "indigo darken-2 text-center rounded",
	    "teal darken-2 text-center rounded",
	    "deep-orange darken-2 text-center rounded",
	    "blue-gray darken-2 text-center rounded",
	    "light-green darken-2 text-center rounded",
	    "orange darken-2 text-center rounded",
	    "gray darken-2 text-center rounded",
	    "cyan darken-2 text-center rounded",
	    "pink darken-2 text-center rounded",
	    "deep-purple darken-2 text-center rounded",
	    "light-blue darken-2 text-center rounded",
	    "brown darken-2 text-center rounded",
	    "purple darken-2 text-center rounded"
	],
	skcolors: [
	    "blue",
	    "green",
	    "red",
	    "indigo",
	    "teal",
	    "deep-orange",
	    "blue-gray",
	    "light-green",
	    "orange",
	    "gray",
	    "cyan",
	    "pink",
	    "deep-purple",
	    "light-blue",
	    "brown",
	    "purple"
	],
	viewBoxSize: 40,
	feature: "tempMin",
	start_year: 1984,
	rangeYear: 5, // 1,
	labelsPos: [{}, {}, {}],
	selectedDate: "Not selected",
	selectedValue: "Not selected",
	spiral_data: [],
	max_values: [],
	orig_data: [],
	sampled_data: [],
	spiral: null,
	year_cycle_data: [],
	hoveredMonth: 1,
	firstMonth: 1,
	year_info: [],
	variation_info: [],
	guide_cycle: [1, 2, 3, 6, 12],
	timeSpan: 12,
	baseYear: 1977,
	endYear: 2017
    }),
    methods: {
	computeCoords(rad, idx) {
	    const divisions = 12
	    const degrees_per_iter = 360 / divisions
	    console.log("[ RADIUS AND IDX ]", this.raw_data[idx])
	    let month = (idx + this.firstMonth) % 12
	    let year_idx
	    this.hoveredMonth = month
	    // let promValues = [0, 0, 0]
	    let promValues = []
	    for (let fidx = 0; fidx < this.features.length; fidx++) {
		promValues[fidx] = 0
	    }
	    let feat_values = [[], [], []]
	    for (let j = 0; j < this.rangeYear; j++) {
		year_idx = j * this.params.points_per_period + (idx % this.params.points_per_period)
		this.year_info[j] = this.sampled_data[year_idx].date.slice(0, -3)
		// this.year_info[j] = this.sampled_data[year_idx].date
		let values = this.sampled_data[year_idx]
		for (let fidx = 0; fidx < this.features.length; fidx++) {
		    console.log(values, this.features[fidx], values[this.features[fidx]])
		    promValues[fidx] += values[this.features[fidx]] / this.rangeYear
		    feat_values[fidx].push(values[this.features[fidx]])
		}
		// for (let i = 1; i < 4; i++) {
		for (let i = 1; i < this.features.length + 1; i++) {
		    rad = values[this.features[i - 1]].map(0, this.max_values[i - 1], 1, this.viewBoxSize * 0.1 * this.rangeYear * 0.5)
		    if (rad == 0) rad = 1
		    this.year_cycle_data[j][i - 1].x = rad * Math.cos((i * 4 * degrees_per_iter * Math.PI) / 180)
		    this.year_cycle_data[j][i - 1].y = rad * Math.sin((i * 4 * degrees_per_iter * Math.PI) / 180)
		}
	    }
	    console.log("[ Variation Info ]:", feat_values, promValues, this.variation_info)
	    for (let j = 0; j < promValues.length; j++) {
		let variation_prom = 0
		for (let i = 0; i < this.rangeYear; i++) {
		    variation_prom += Math.abs(feat_values[j][i] - promValues[j]) ** 2
		}
		this.variation_info[j] = ( variation_prom / promValues.length ** 2).toFixed(2)
	    }
	},
	showDetails(values, index) {
	    this.computeCoords(values[2], index)
	    this.selectedDate = this.sampled_data[index].date.slice(0, -3)
	    this.selectedValue = this.sampled_data[index][this.feature]
	},
	renderSpiral() {
	    var points = []
	    var cycles = this.rangeYear
	    console.log("[ Raw data ]:", this.raw_data)
	    this.getPeriodAdvice()
	    let sampled_data = this.raw_data
	    this.sampled_data = sampled_data
	    let raw_data = sampled_data
	    let size
	    console.log("[ Sampled data ]:", raw_data)
	    for (let index = 0; index < this.params.points_per_period * cycles; index++) {
		if (index < raw_data.length) {
		    // console.log("DEBUG: ", index, this.params.points_per_period, cycles, raw_data[index][this.feature], this.feature);
		    size = raw_data[index][this.feature]
		    points.push([index, size])
		}
	    }
	    var spiral1 = new Spiral("points")
	    spiral1.setParam("numberOfPoints", this.params.points_per_period * cycles)
	    spiral1.setParam("period", this.params.points_per_period)
	    spiral1.setParam("svgHeight", window.innerHeight * 0.7)
	    spiral1.setParam("svgWidth", 650)
	    spiral1.setParam("spacing", 8)
	    spiral1.setParam("hoverFunction", this.showDetails)
	    spiral1.setParam("radiusParam", this.params.radius)
	    spiral1.option.data = points
	    spiral1.option.dates = raw_data
	    let first_date_month = parseInt(raw_data[0].date.split("-")[1])
	    console.log("[ First date ]: ", first_date_month)
	    this.spiral_data = sampled_data
	    this.firstMonth = first_date_month - 1
	    spiral1.option.offset = first_date_month - 1
	    spiral1.adjustData()
	    this.spiral = spiral1
	},
	getPolygonCoords(idx) {
	    return this.year_cycle_data[idx].map(line => { return line.x + "," + line.y }).join(" ")
	},
	getSpiralCoords() {
	    return this.spiral1.option.data.map(point => { return point[0] + "," + point[1] }).join(" ")
	},
	async getPeriodAdvice() {
	    let segment_recommendation = await axios.get(
		"http://localhost:8080/timespan/" + this.dataset + "/" + this.station + "/MS",
		{ crossdomain: true }
	    )
	    console.log("[ Cyclity detected ]: ", segment_recommendation.data.status);
	    // if (segment_recommendation.data.status == "True") {
	    // }
	    this.guide_cycle = segment_recommendation.data.periods
	    if (this.initialState) {
		this.timeSpan = parseInt(segment_recommendation.data.timespan)
		this.params.points_per_period = this.timeSpan
		this.initialState = false
	    }
	    // if (this.guide_cycle > this.raw_data.length) {
	    // 	this.guide_cycle = this.raw_data.length
	    // }
	    // if (this.timeSpan > this.raw_data.length) {
	    // 	this.timeSpan = this.raw_data.length
	    // }
	    // if (this.params.points_per_period > this.raw_data.length) {
	    // 	this.params.points_per_period = this.raw_data.length
	    // }
	    if (this.timeSpan > this.periodsBase) {
		this.periodsMax = Math.ceil(this.timeSpan / 12) * 12
	    }
	    console.log("[ Guiding Cycle Periods ]:", this.guide_cycle)
	    console.log("[ Current Time span ]:", this.timeSpan)
	    console.log("[ Points Per Period ]:", this.params.points_per_period)
	    console.log("[ Raw Data Length ]:", this.raw_data.length)
	},
	async showDatasetSpiral() {
	    this.datasetSelected = true
	    for (let index = 0; index < this.rangeYear; index++) {
		this.year_cycle_data.push([
		    { x: 1, y: 1 },
		    { x: 1, y: 1 },
		    { x: 1, y: 1 }
		])
		this.year_info.push(this.start_year + index)
	    }
	    // for (let fidx = 0; fidx < this.features.length; fidx++) {
	    // 	// this.variation_info = [0, 0, 0]
	    // 	this.variation_info[fidx] = 0
	    // }
	    console.log("[ Loading... ]", this.year_cycle_data)
	    let data = await axios.get(
		"http://localhost:8080/data/" + this.dataset + "/" + this.station + "/MS",
		{ crossdomain: true }
	    )
	    let raw_data = data.data
	    // this.max_values = data.headers["max-values"].split(",").map(parseFloat)
	    this.baseYear = parseInt(raw_data[0].date.split("-")[0])
	    this.endYear = parseInt(raw_data[raw_data.length - 1].date.split("-")[0])
	    let first_date_year = this.baseYear
	    console.log("[ First year ]:", raw_data[0].date, first_date_year)
	    console.log("[ Base Year, End Year ]:", this.baseYear, ",", this.endYear)
	    this.start_year = first_date_year
	    this.featureitems = []
	    this.features = []
	    for (const fitem in raw_data[0]) {
		if ( fitem !== "date" ) {
		    this.featureitems.push({ text: fitem, value: fitem });
		    this.features.push(fitem);
		}
	    }
	    this.feature = this.features[0]
	    for (let fidx = 0; fidx < this.features.length; fidx++) {
		// this.variation_info = [0, 0, 0]
		this.variation_info[fidx] = 0
	    }
	    console.log("[ Feature Items ]:", this.featureitems);
	    console.log("[ Features ]:", this.features);
	    console.log("[ Default Feature ]:", this.feature);
	    this.max_values = this.features.map(feat => d3.max(raw_data, d => d[feat]))
	    console.log("[ Max Values ]:", this.max_values)
	    this.raw_data = raw_data
	    this.orig_data = raw_data.slice()
	    // this.orig_data = raw_data
	    this.renderSpiral()
	    this.spiral.render()
	    let rad = 2
	    let glyph_rad = rad + 5
	    const M_PI = Math.PI
	    const divisions = 12
	    const degrees_per_iter = 360 / divisions
	    for (let i = 1; i < 4; i++) {
		rad = Math.random() * 10 + 1
		this.lines[i - 1].x =
		    rad * Math.cos((i * 4 * degrees_per_iter * M_PI) / 180)
		this.lines[i - 1].y =
		    rad * Math.sin((i * 4 * degrees_per_iter * M_PI) / 180)
		this.labelsPos[i - 1] = {
		    x: glyph_rad * Math.cos((i * 4 * degrees_per_iter * M_PI) / 180),
		    y: glyph_rad * Math.sin((i * 4 * degrees_per_iter * M_PI) / 180)
		}
	    }
	}
    },
    computed: {
	line_points: function() {
	    return this.lines.map(line => { return line.x + "," + line.y }).join(" ")
	},
	year_items: function() {
	    let lowerBound = this.baseYear;
	    let upperBound = this.endYear - Math.floor(this.rangeYear * this.params.points_per_period / 12);
	    if (upperBound < lowerBound) upperBound = this.endYear;
	    return Array.from(new Array(upperBound - lowerBound + 1), (x, i) => i + lowerBound);
	},
	// rangeYears: function() {
	//     let lowerBound = 1
	//     let upperBound = 15
	//     return Array.from(new Array(upperBound - lowerBound + 1), (x, i) => i + lowerBound)
	// },
	end_year: function() {
	    let res = this.start_year + (this.rangeYear * this.params.points_per_period) / 12
	    return this.start_year ? Math.round(res) : null
	}
    },
    mounted: function() {
	this.dataset = this.$route.params.dataset;
	this.station = this.$route.params.station;
	AppBus.$emit('disabled-buttons', false);
	AppBus.$emit('update-button-home', false, true);
	AppBus.$emit('update-button-net', false, true);
	AppBus.$emit('update-button-visualize', false, true);
	AppBus.$emit('update-button-stats', false, true);
	AppBus.$emit('update-button-spiral', true, false);
	document.getElementById("dynNet").href=`/net/${this.dataset}/${this.station}`;
	document.getElementById("dynVisualize").href=`/visualize/${this.dataset}/${this.station}`;
	document.getElementById("dynStats").href=`/stats/${this.dataset}/${this.station}`;
	document.getElementById("dynSpiral").href=`/spiral/${this.dataset}/${this.station}`;
	this.items = [{ text: this.station, value: this.station }]
	console.log("[ Mounted Radial View ]: (", this.dataset, ",", this.station, ")");
	this.showDatasetSpiral()
    },
    watch: {
	"params.points_per_period": function() {
	    this.cyclesMax = Math.floor((this.endYear - this.baseYear) / (this.params.points_per_period / 12));
	    if ( this.rangeYear > this.cyclesMax ) {
		this.rangeYear = this.cyclesMax;
	    }
	    console.log("[ WATCH POINTS PER PERIOD ]");
	    this.renderSpiral();
	    this.spiral.redraw();
	},
	"params.radius": function() {
	    console.log("[ WATCH RADIUS ]");
	    this.renderSpiral();
	    this.spiral.redraw();
	},
	feature() {
	    console.log("[ WATCH FEATURE ]");
	    this.renderSpiral();
	    this.spiral.redraw();
	},
	end_year(newValue) {
	    console.log("[ WATCH END_YEAR ]", newValue);
	    this.raw_data = this.orig_data.filter(x => { return x.date > `${this.start_year}-01-01` });
	    this.renderSpiral();
	    this.spiral.redraw();
	},
	rangeYear() {
	    console.log("[ WATCH CYCLES ]");
	    this.cyclesMax = Math.floor((this.endYear - this.baseYear) / (this.params.points_per_period / 12));
	    if ( this.rangeYear > this.cyclesMax ) {
		this.rangeYear = this.cyclesMax;
	    }
	    this.renderSpiral();
	    this.spiral.redraw();
	    this.year_cycle_data = [];
	    for (let index = 0; index < this.rangeYear; index++) {
		this.year_cycle_data.push([
		    { x: 1, y: 1 },
		    { x: 1, y: 1 },
		    { x: 1, y: 1 }
		]);
		this.year_info.push(this.start_year + index);
	    }
	    for (let fidx = 0; fidx < this.features.length; fidx++) {
		// this.variation_info = [0, 0, 0]
		this.variation_info[fidx] = 0
	    }
	}
    }
}
</script>

<style>
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
</style>
