<template>
  <v-container class="my-6" fluid>
    <v-row
      dense
      class="text-center"
      justify="center"
      align="center"
      v-if="!datasetSelected">
      <v-col cols="3">
        <h1>Dataset:</h1>
      </v-col>
      <v-col cols="3">
        <v-select
          v-model="dataset"
          :items="items"
          item-text="text"
          item-value="value"
          label="Select"
          persistent-hint
          single-line></v-select>
      </v-col>
      <v-col cols="2">
        <v-btn color="primary" @click="showDatasetSpiral">Use</v-btn>
      </v-col>
    </v-row>
    <v-row dense align="center" justify="center" v-if="datasetSelected">
      <h2>Dataset: {{ dataset.toUpperCase() }}</h2>
      <v-col cols="12" class="text-center">
        <span>
	  Max Value for Range is 10 due to visualization size reasons.
	</span>
      </v-col>
      <v-col cols="2">
        <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      </v-col>
      <v-col cols="3">
        <v-select
          v-model="feature"
          :items="[
		  { text: 'Precipitation', value: 'precipitation' },
		  { text: 'Temp Max', value: 'tempMax' },
		  { text: 'Temp Min', value: 'tempMin' }
		  ]"
          item-text="text"
          item-value="value"
          label="Feature"
          placeholder="Select a feature"
          outlined>
	</v-select>
      </v-col>
      <v-col cols="3">
        <v-select
          v-model="start_year"
          :items="year_items"
          item-text="text"
          item-value="value"
          label="Start year"
          placeholder="Select a year"
          outlined>
	</v-select>
      </v-col>
      <v-col cols="3">
        <v-text-field
          v-model="end_year"
          label="End year"
          placeholder="Select a year"
          outlined
          readonly>
	</v-text-field>
      </v-col>
    </v-row>
    <v-row dense class="text-center text-h6" v-if="datasetSelected">
      <v-col>
        Selected date: {{ selectedDate }} - Value:
        {{ selectedValue }}

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
                            <v-icon
                              color="primary"
                              dark
                              v-bind="attrs"
                              v-on="on">
                              mdi-help-circle-outline
                            </v-icon>
                          </template>
                          <span>
			    Segments used for every cycle in the spiral
			  </span>
                        </v-tooltip>
                      </div>
                    </v-list-item-title>
                  </v-col>
                  <v-col cols="11">
                    <vue-slider
                      v-model="params.points_per_period"
                      :min="2"
                      :max="36"
                      :step="1"
                      marks
                      hide-label>
                      <template v-slot:step="{ label, active }">
                        <div :class="['custom-step', { active }]"></div>
                        <div
                          :class="[
				  'custom-step-bar',
				  guide_cycle.includes(label) ? 'active' : ''
				  ]">
			</div>
                      </template>
                    </vue-slider>
                    <!-- <v-slider
			 v-model="params.points_per_period"
			 max="365"
			 min="12">
			 </v-slider> -->
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
                            <v-icon
                              color="primary"
                              dark
                              v-bind="attrs"
                              v-on="on">
                              mdi-help-circle-outline
                            </v-icon>
                          </template>
                          <span>Númber of cycles on the spiral</span>
                        </v-tooltip>
                      </div>
                    </v-list-item-title>
                  </v-col>
                  <v-col cols="11">
                    <vue-slider v-model="rangeYear" :min="2" :max="15">
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
                            <v-icon
                              color="primary"
                              dark
                              v-bind="attrs"
                              v-on="on">
                              mdi-help-circle-outline
                            </v-icon>
                          </template>
                          <span>
			    Radius of the spiral (minimum and maximum values
                            are set due to visualization reasons).
			  </span>
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
          <v-col>
            <div class="blue darken-2 text-center rounded">
              <span class="white--text">
		Precipitation
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon color="white" dark v-bind="attrs" v-on="on">
                      mdi-help-circle-outline
                    </v-icon>
                  </template>
                  <span>
                    You can find a variation percentage for the Precipitation
                    variable. This indicates how much the values change for
                    every cycle of the spiral.
                  </span>
                </v-tooltip>
              </span>
            </div>
          </v-col>
          <v-col>
            <div class="green darken-2 text-center rounded">
              <span class="white--text">
		Temp. Min
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon color="white" dark v-bind="attrs" v-on="on">
                      mdi-help-circle-outline
                    </v-icon>
                  </template>
                  <span>
                    Above you can find a variation percentage for the Minimim
                    Temperature variable. This indicates how much the values
                    change for every cycle of the spiral.
                  </span>
                </v-tooltip>
              </span>
            </div>
          </v-col>
          <v-col>
            <div class="red darken-2 text-center rounded">
              <span class="white--text">
		Temp. Max
                <v-tooltip top>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon color="white" dark v-bind="attrs" v-on="on">
                      mdi-help-circle-outline
                    </v-icon>
                  </template>
                  <span>
                    Above you can find a variation percentage for the Maximum
                    Temperature variable. This indicates how much the values
                    change for every cycle of the spiral.
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
                <polygon
		  :points="getPolygonCoords(index)" fill="gray" fill-opacity="0.3" stroke="gray" stroke-width="0.5">
		</polygon>
                <line x1="0" y1="0" :x2="year_lines[0].x" :y2="year_lines[0].y" stroke="blue" stroke-width="0.5" />
                <line x1="0" y1="0" :x2="year_lines[1].x" :y2="year_lines[1].y" stroke="red" stroke-width="0.5" />
                <line x1="0" y1="0" :x2="year_lines[2].x" :y2="year_lines[2].y" stroke="green" stroke-width="0.5" />
                <!-- <text v-for="(pos, i) in labelsPos" :x="pos.x" :y="pos.y" v-bind:key="i" font-size="3px">
		     {{ features[i] }}
		     </text>
                <text :x="labelsPos[0].x" :y="labelsPos[0].y" font-size="3px">
		  Precipitation
		</text>
		<text :x="labelsPos[1].x" :y="labelsPos[1].y" font-size="3px">
		  Temp. Máxima
		</text>
		<text :x="labelsPos[2].x" :y="labelsPos[2].y" font-size="3px">
		  Temp. Mínima
		</text> -->
              </g>
            </svg>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
// @ is an alias to /src
import Spiral from "@/views/point_spiral"
import * as d3 from "d3"
import axios from "axios"
import VueSlider from "vue-slider-component"
import "vue-slider-component/theme/default.css"

export default {
    name: "Home",
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
	dataset: "majes",
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
	features: ["precipitation", "tempMax", "tempMin"],
	viewBoxSize: 40,
	feature: "tempMin",
	start_year: 1984,
	rangeYear: 5,
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
	guide_cycle: [1, 2, 3, 6, 12]
    }),
    methods: {
	calculateCoords(rad, idx) {
	    const divisions = 12
	    const degrees_per_iter = 360 / divisions
	    console.log("Radius and idx", this.raw_data[idx])
	    let month = (idx + this.firstMonth) % 12
	    let year_idx
	    // console.log("Month: ", month, idx)
	    this.hoveredMonth = month

	    let promValues = [0, 0, 0]
	    let feat_values = [[], [], []]
	    for (let j = 0; j < this.rangeYear; j++) {
		year_idx =
		    j * this.params.points_per_period +
		    (idx % this.params.points_per_period)

		// console.log("Year ", year_idx)
		this.year_info[j] = this.sampled_data[year_idx].date.slice(0, -3)

		let values = this.sampled_data[year_idx]

		for (let fidx = 0; fidx < this.features.length; fidx++) {
		    console.log(values, this.features[fidx], values[this.features[fidx]])
		    promValues[fidx] += values[this.features[fidx]] / this.rangeYear
		    feat_values[fidx].push(values[this.features[fidx]])
		}

		for (let i = 1; i < 4; i++) {
		    // rad = Math.random() * 20 + 15

		    rad = values[this.features[i - 1]].map(
			0,
			this.max_values[i - 1],
			1,
			this.viewBoxSize * 0.1 * this.rangeYear * 0.5
		    )
		    if (rad == 0) rad = 1
		    this.year_cycle_data[j][i - 1].x =
			rad * Math.cos((i * 4 * degrees_per_iter * Math.PI) / 180)
		    this.year_cycle_data[j][i - 1].y =
			rad * Math.sin((i * 4 * degrees_per_iter * Math.PI) / 180)
		}
	    }
	    console.log(feat_values, promValues)
	    for (let j = 0; j < promValues.length; j++) {
		// const element = promValues[j]
		let variation_prom = 0
		for (let i = 0; i < this.rangeYear; i++) {
		    variation_prom += Math.abs(feat_values[j][i] - promValues[j]) ** 2
		}
		this.variation_info[j] = (
		    variation_prom /
			promValues.length ** 2
		).toFixed(2)
	    }
	},

	showDetails(values, index) {
	    // console.log("Hover:", values[2], index)
	    // console.log("New coords", this.calculateCoords(values[2], 1))
	    this.calculateCoords(values[2], index)
	    // console.log(this.lines[0])
	    this.selectedDate = this.sampled_data[index].date
	    this.selectedValue = this.sampled_data[index][this.feature]
	},

	renderSpiral() {
	    // var data = []
	    var points = []
	    var cycles = this.rangeYear
	    // var start_year = 2009

	    let sampled_data = this.sampleArrayByYear(
		this.raw_data,
		12 / this.params.points_per_period
	    )
	    console.log("Original data", this.raw_data)

	    this.sampled_data = sampled_data

	    let size
	    let raw_data = sampled_data
	    // let feature = this.feature
	    let feat_idx = this.features.indexOf(this.feature)
	    console.log("data to visualize: ", raw_data)

	    // // let offset = 12 / this.periods
	    // let simplifiedRawData = []
	    // for (let index = 0; index < raw_data.length; index += 2) {
	    //   console.log(raw_data[index].precipitation, index, raw_data.length)
	    //   let newDate = {
	    //     date: raw_data[index].date,
	    //     precipitation:
	    //       raw_data[index].precipitation + raw_data[index + 1].precipitation,
	    //     tempMin: raw_data[index].tempMin + raw_data[index + 1].tempMin,
	    //     tempMax: raw_data[index].tempMax + raw_data[index + 1].tempMax
	    //   }
	    //   simplifiedRawData.push(newDate)
	    // }

	    // raw_data = simplifiedRawData

	    for (
		let index = 0;
		index < this.params.points_per_period * cycles;
		index++
	    ) {
		// size = Math.floor(Math.random() * 10) + 1
		// size = Math.floor(Math.random() * 10) + 1
		size = raw_data[index][this.feature].map(
		    0,
		    this.max_values[feat_idx],
		    1,
		    10
		)
		size = raw_data[index][this.feature]
		// var mes = index % 12
		// var año = parseInt(start_year + index / 12)
		// data.push({
		//   date: `${año}-${("0" + (mes + 1)).slice(-2)}`,
		//   value: size
		// })
		points.push([index, size])
	    }

	    this.getPeriodRecommendations()

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
	    console.log("Primera fecha: ", first_date_month)

	    this.spiral_data = sampled_data
	    this.firstMonth = first_date_month - 1
	    spiral1.option.offset = first_date_month - 1
	    // console.log(data)
	    spiral1.adjustData()
	    // spiral1.render()
	    this.spiral = spiral1
	},
	getPolygonCoords(idx) {
	    return this.year_cycle_data[idx]
		.map(line => {
		    return line.x + "," + line.y
		})
		.join(" ")
	},
	getSpiralCoords() {
	    return this.spiral1.option.data
		.map(point => {
		    return point[0] + "," + point[1]
		})
		.join(" ")
	},
	async getPeriodRecommendations() {
	    let feat_idx = this.features.indexOf(this.feature)
	    let segment_recommendation = await axios.get(
		`http://localhost:8081/data/${this.dataset}/period?feature=${feat_idx}`,
		{ crossdomain: true }
	    )

	    this.guide_cycle = segment_recommendation.data.periods
	},
	sampleArrayByYear(data, x) {
	    const result = []

	    let currYear, currMonth, currData, newData
	    for (let i = 0; i < data.length; i++) {
		newData = false

		const date = new Date(data[i].date)
		const year = date.getFullYear()
		const month = date.getMonth()

		if (
		    currData &&
			(year > currYear ||
			 (year === currYear &&
			  (month - currMonth >= x || month < currMonth)))
		) {
		    result.push(currData)
		    currData = null
		}

		if (
		    !currData ||
			year > currYear ||
			(year === currYear && month < currMonth)
		) {
		    currYear = year
		    currMonth = month
		    currData = {
			date: `${year}-${(month + 1).toString().padStart(2, "0")}-01`
		    }
		    newData = true
		}

		if (newData || data[i].precipitation > currData.precipitation) {
		    currData.precipitation = data[i].precipitation
		}

		if (newData || data[i].tempMax > currData.tempMax) {
		    currData.tempMax = data[i].tempMax
		}

		if (newData || data[i].tempMin > currData.tempMin) {
		    currData.tempMin = data[i].tempMin
		}
	    }

	    if (currData) {
		result.push(currData)
	    }

	    return result
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
	    this.variation_info = [0, 0, 0]
	    console.log("Loading...", this.year_cycle_data)
	    let data = await axios.get(
		"http://localhost:8081/data/" + this.dataset + "/scale",
		{
		    crossdomain: true
		}
	    )

	    let raw_data = data.data
	    // this.max_values = data.headers["max-values"].split(",").map(parseFloat)
	    let first_date_year = parseInt(raw_data[0].date.split("-")[0])
	    console.log("Primer año", raw_data[0].date, first_date_year)
	    this.start_year = first_date_year

	    this.max_values = this.features.map(feat =>
		d3.max(raw_data, d => d[feat])
	    )
	    console.log(this.max_values)
	    this.raw_data = raw_data
	    this.orig_data = raw_data.slice()

	    console.log(raw_data)

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
	    return this.lines
		.map(line => {
		    return line.x + "," + line.y
		})
		.join(" ")
	},
	year_items: function() {
	    let lowerBound = this.start_year
	    let upperBound = 2013
	    return Array.from(
		new Array(upperBound - lowerBound + 1),
		(x, i) => i + lowerBound
	    )
	},
	rangeYears: function() {
	    let lowerBound = 1
	    let upperBound = 15
	    return Array.from(
		new Array(upperBound - lowerBound + 1),
		(x, i) => i + lowerBound
	    )
	},
	end_year: function() {
	    let res =
		this.start_year + (this.rangeYear * this.params.points_per_period) / 12

	    return this.start_year ? Math.round(res) : null
	}
    },
    watch: {
	"params.points_per_period": function() {
	    this.renderSpiral()
	    this.spiral.redraw()
	},
	"params.radius": function() {
	    this.renderSpiral()
	    this.spiral.redraw()
	},
	feature() {
	    this.renderSpiral()
	    this.spiral.redraw()
	},
	end_year(newValue) {
	    if (newValue > 2014) {
		this.end_year = 2014
		this.rangeYear = 2014 - this.start_year
	    }
	    this.raw_data = this.orig_data.filter(x => {
		return x.date > `${this.start_year}-01-01`
	    })
	    this.renderSpiral()
	    this.spiral.redraw()
	},
	rangeYear() {
	    this.renderSpiral()
	    this.spiral.redraw()
	    this.year_cycle_data = []
	    for (let index = 0; index < this.rangeYear; index++) {
		this.year_cycle_data.push([
		    { x: 1, y: 1 },
		    { x: 1, y: 1 },
		    { x: 1, y: 1 }
		])
		this.year_info.push(this.start_year + index)
	    }
	    this.variation_info = [0, 0, 0]
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
