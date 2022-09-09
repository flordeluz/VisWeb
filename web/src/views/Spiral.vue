<template>
  <v-container class="my-6" fluid>
    <v-row
      dense
      class="text-center"
      justify="center"
      align="center"
      v-if="!datasetSelected"
    >
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
          single-line
        ></v-select>
      </v-col>
      <v-col cols="2">
        <v-btn color="primary" @click="showDatasetSpiral">Use</v-btn>
      </v-col>
    </v-row>
    <v-row dense align="center" justify="center" v-if="datasetSelected">
      <v-col cols="12" class="text-center">
        <span
          >Max Value for Range is 10 due to visualization size reasons.</span
        >
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
          outlined
        ></v-select>
      </v-col>
      <v-col cols="2">
        <v-select
          v-model="start_year"
          :items="year_items"
          item-text="text"
          item-value="value"
          label="Start year"
          placeholder="Select a year"
          outlined
        ></v-select>
      </v-col>
      <v-col cols="2">
        <v-select
          v-model="rangeYear"
          :items="rangeYears"
          item-text="text"
          item-value="value"
          label="Range"
          placeholder="Select a Range"
          outlined
        ></v-select>
      </v-col>
      <v-col cols="2">
        <v-text-field
          v-model="end_year"
          label="End year"
          placeholder="Select a year"
          outlined
          readonly
        ></v-text-field>
      </v-col>
    </v-row>

    <v-row dense class="text-center text-h6" v-if="datasetSelected">
      <v-col>
        Selected date: {{ selectedDate }} - Value:
        {{ selectedValue }}
      </v-col>
    </v-row>
    <v-row class="text-center align-center" v-if="datasetSelected">
      <v-col>
        <div id="chart"></div>
      </v-col>
      <v-col class="text-center">
        <v-row class="text-center mb-10">
          <v-col>
            <div class="blue darken-2 text-center rounded">
              <span class="white--text">Precipitacion</span>
            </div>
          </v-col>
          <v-col>
            <div class="green darken-2 text-center rounded">
              <span class="white--text">Temp. Min</span>
            </div>
          </v-col>
          <v-col>
            <div class="red darken-2 text-center rounded">
              <span class="white--text">Temp. Max</span>
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col
            v-for="(year_lines, index) in year_cycle_data"
            v-bind:key="index"
            :cols="rangeYear > 5 ? '2' : ''"
          >
            {{ year_info[index] }}
            <svg
              width="100%"
              height="200"
              :viewBox="
                `-${viewBoxSize / 2} -${viewBoxSize /
                  2} ${viewBoxSize} ${viewBoxSize}`
              "
              xmlns="http://www.w3.org/2000/svg"
            >
              <g>
                <polygon
                  :points="getPolygonCoords(index)"
                  fill="gray"
                  fill-opacity="0.3"
                  stroke="gray"
                  stroke-width="0.5"
                ></polygon>
                <line
                  x1="0"
                  y1="0"
                  :x2="year_lines[0].x"
                  :y2="year_lines[0].y"
                  stroke="blue"
                  stroke-width="0.5"
                />
                <line
                  x1="0"
                  y1="0"
                  :x2="year_lines[1].x"
                  :y2="year_lines[1].y"
                  stroke="red"
                  stroke-width="0.5"
                />
                <line
                  x1="0"
                  y1="0"
                  :x2="year_lines[2].x"
                  :y2="year_lines[2].y"
                  stroke="green"
                  stroke-width="0.5"
                />

                <!-- <text
              v-for="(pos, i) in labelsPos"
              :x="pos.x"
              :y="pos.y"
              v-bind:key="i"
              font-size="3px"
            >
              {{ features[i] }}
            </text> -->
                <!-- <text :x="labelsPos[0].x" :y="labelsPos[0].y" font-size="3px">
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
import Spiral from '@/views/point_spiral'
import * as d3 from 'd3'
import axios from 'axios'

export default {
  name: 'Home',
  data: () => ({
    dataset: 'majes',
    items: [
      { text: 'MAJES', value: 'majes' },
      { text: 'CHIGUATA', value: 'chiguata' },
      { text: 'JOYA', value: 'joya' },
      { text: 'PAMPILLA', value: 'pampilla' }
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
    features: ['precipitation', 'tempMax', 'tempMin'],
    viewBoxSize: 40,
    feature: 'tempMin',
    start_year: 1984,
    rangeYear: 5,
    labelsPos: [{}, {}, {}],
    selectedDate: 'Not selected',
    selectedValue: 'Not selected',
    spiral_data: [],
    max_values: [],
    orig_data: [],
    spiral: null,
    year_cycle_data: [],
    hoveredMonth: 1,
    firstMonth: 1,
    year_info: []
  }),
  methods: {
    calculateCoords(rad, idx) {
      const divisions = 12
      const degrees_per_iter = 360 / divisions
      console.log('Radius and idx', this.raw_data[idx])
      let month = (idx + this.firstMonth) % 12
      let year_idx
      // console.log('Month: ', month, idx)
      this.hoveredMonth = month
      for (let j = 0; j < this.rangeYear; j++) {
        year_idx = j * 12 + (idx % 12)

        // console.log('Year ', year_idx)
        this.year_info[j] = this.raw_data[year_idx].date.slice(0, -3)

        let values = this.raw_data[year_idx]
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
    },

    showDetails(values, index) {
      // console.log('Hover:', values[2], index)
      // console.log('New coords', this.calculateCoords(values[2], 1))
      this.calculateCoords(values[2], index)
      // console.log(this.lines[0])
      this.selectedDate = this.raw_data[index].date
      this.selectedValue = this.raw_data[index][this.feature]
    },

    renderSpiral() {
      // var data = []
      var points = []
      var cycles = this.rangeYear
      // var start_year = 2009
      let size
      let raw_data = this.raw_data
      // let feature = this.feature
      let feat_idx = this.features.indexOf(this.feature)

      for (let index = 0; index < 12 * cycles; index++) {
        // size = Math.floor(Math.random() * 10) + 1
        // size = Math.floor(Math.random() * 10) + 1
        size = raw_data[index][this.feature].map(
          0,
          this.max_values[feat_idx],
          1,
          10
        )
        // var mes = index % 12
        // var año = parseInt(start_year + index / 12)
        // data.push({
        //   date: `${año}-${('0' + (mes + 1)).slice(-2)}`,
        //   value: size
        // })
        points.push([index, size])
      }

      var spiral1 = new Spiral('points')
      spiral1.setParam('numberOfPoints', 12 * cycles)
      spiral1.setParam('period', 12)
      spiral1.setParam('svgHeight', window.innerHeight * 0.7)
      spiral1.setParam('svgWidth', 650)
      spiral1.setParam('spacing', 8)
      spiral1.setParam('hoverFunction', this.showDetails)

      spiral1.option.data = points
      spiral1.option.dates = raw_data

      let first_date_month = parseInt(raw_data[0].date.split('-')[1])
      console.log('Primera fecha: ', first_date_month)

      this.spiral_data = raw_data
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
          return line.x + ',' + line.y
        })
        .join(' ')
    },
    getSpiralCoords() {
      return this.spiral1.option.data
        .map(point => {
          return point[0] + ',' + point[1]
        })
        .join(' ')
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
      console.log('Loading...', this.year_cycle_data)
      let data = await axios.get(
        'http://localhost:8080/data/' + this.dataset + '/scale',
        { crossdomain: true }
      )
      console.log(
        'Headers: ',
        data.headers['max-values'].split(',').map(parseFloat)
      )

      this.max_values = data.headers['max-values'].split(',').map(parseFloat)
      let raw_data = data.data
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
          return line.x + ',' + line.y
        })
        .join(' ')
    },
    year_items: function() {
      let lowerBound = 1984
      let upperBound = 2013
      return Array.from(
        new Array(upperBound - lowerBound + 1),
        (x, i) => i + lowerBound
      )
    },
    rangeYears: function() {
      let lowerBound = 1
      let upperBound = 10
      return Array.from(
        new Array(upperBound - lowerBound + 1),
        (x, i) => i + lowerBound
      )
    },
    end_year: function() {
      return this.start_year ? this.start_year + this.rangeYear : null
    }
  },
  watch: {
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
</style>
