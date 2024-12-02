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
  <v-row>
    <v-col cols="1.5">
      <table class="blockTable pastTable firstRow text-center">
        <tr v-for="operation in pastTable" :key="operation.method">
          <td class="border slideOp" @click="changeVis(operation)" :id="`tab-${operation.method}`">
            <span class="text-h5">{{ operation.fullName }}</span>
          </td>
        </tr>
      </table>
    </v-col>
    <v-col v-if="!showSpiral">
      <v-row>
        <!-- <v-col :cols="seePresentChart ? 3 : ''"> -->
        <v-col cols="10">
          <!-- <div id="graph1" class="firstRow" style="height: 588px; width: 1008px; position:relative; border: 4px solid #73AD21; border-radius:8px" -->
	  <!--      ref="timeChart" :diameter="200"></div> -->
          <div id="graph1" class="firstRow" style="height: 80vh; width: 1080px; position:relative; border: 4px solid #73AD21; border-radius:8px"
	       ref="timeChart" :diameter="200"></div>
	  <!--
          <feature-viscovery ref="guide" :auto-aim-delay="500" :diameter="80" background-color="rgba(10,10,10, 0.719)">
            <h3>Guía</h3>
            <div v-html="guide[currentGuide] ? guide[currentGuide].text : ''"></div>
          </feature-viscovery>
	  -->
        </v-col>
        <v-col v-if="seePresentChart">
          <div id="graph2" class="firstRow" style="position:relative; border: 4px solid #73AD21;"></div>
        </v-col>
      </v-row>
    </v-col>
    <v-col v-else>
      <div id="chart"></div>
    </v-col>
    <v-col cols="1.5">
      <table class="blockTable firstRow">
        <tr v-for="operation in futureTable" :key="operation.method">
          <td class="border slideOp" @click="changeVisFromFuture(operation)" :id="`tab-${operation.method}`">
            <span class="text-h5">{{ operation.fullName }}</span>
          </td>
        </tr>
      </table>
    </v-col>
  </v-row>

  <!-- /* Raw botton and action description */
  <v-row class="pb-xl-16" align="center">
    <div id="op-raw">
      <table>
        <tr>
          <td style="width:100px;background-color: #ff88004d" class="border text-center">
            Raw Data
          </td>
        </tr>
      </table>
    </div>
    <v-col class="pa-1">
      <div class="text-h6 pa-0 text-center" :id="`tab-${operation.method}`" ref="currentOperation">
        Current Operation:
        {{ this.infoOperation ? this.infoOperation : 'No Selected' }}
      </div>
    </v-col>
  </v-row>
  /* End raw botton and action description */ -->

  <!-- /* Diagram */
  <v-row style="height:26vh" class="pt-10 pt-xl-16">
    <v-col class="fill-height">
      <operator-diagram v-on:operatorSelected="doTask" v-bind:newTask="newTask" v-on:rendered="redrawLines"
			:recommendations="recommendations" />
    </v-col>
  </v-row>
  <v-row class="pt-4">
    <v-col align-self="end" ref="macroTaskContainer">
      <diagram ref="macroTaskDiagram" v-on:taskSelected="selectedTask" v-on:macrotaskRec="recMacrotask"
	       :dataset="dataset" :station="station" :recommendations="recommendations" :algorithms="algorithms" />
    </v-col>
  </v-row>
  <v-dialog v-model="dialog" width="500">
    <v-card mt="4">
      <v-card-title class="headline grey lighten-2">
        Task Parameters
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
                <v-select label="Feature" v-model="feature"
			  :items="[
				  { text: 'Precipitation', value: 0 },
				  { text: 'Temp Max', value: 1 },
				  { text: 'Temp Min', value: 2 }
				  ]"
			  ref="feature" v-if="main_operation === 'trend' ||
					      main_operation === 'seasonality' ||
					      main_operation === 'cyclicity'"
			  :rules="[v => !!v || 'Required']" />
              </v-col>
              <v-col>
                <v-btn @click="selectedMethod" large color="primary">
                  Apply</v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
  /* End diagram */ -->
  
</v-container>
</template>

<style>
@import "~metrics-graphics/dist/metricsgraphics.css";
</style>

<script>
// import MG from "metrics-graphics"
import axios from "axios"
import Spiral from "@/views/point_spiral"

let CanvasJS = window.CanvasJS

// // import Diagram from "../components/Diagram.vue"
// // import OperatorDiagram from "../components/OperatorDiagram.vue"
// import FeatureViscovery from "feature-viscovery"
import LeaderLine from "leader-line-new"
// // import tippy from "tippy.js"
// // import "tippy.js/dist/tippy.css" // optional for styling
// import "feature-viscovery/dist/feature-viscovery.esm.css" // optional for styling
// // import Operations from "../components/Operations.vue"

export default {
    components: { /* Diagram, OperatorDiagram, FeatureViscovery */ },
    data: () => ({
	dataset: "",
	station: null,
	recommendations: {},
	algorithms: {},
	tareasHechas: [],
	reUpdateMacroTask: [],
	chart: null,
	chart2: null,
	tempMaxData: [],
	tempMinData: [],
	precipitationData: [],
	seePresentChart: false,
	chart1AxisX: {},
	chart2AxisX: {},
	operation: {},
	history: [],
	dialog: false,
	isClean: false,
	isCleanFT: false,
	n_comp: "",
	factor: "",
	feature: "",
	main_operation: "",
	main_opName: "",
	main_method: "",
	newTask: "",
	pastTable: [],
	futureTable: [],
	infoOperation: "",
	tableIdLines: [],
	tableLines: [],
	linesGravity: 50,
	reduceSelected: false,
	//features: ["precipitation", "tempMin", "tempMax"],
	//legends: ["Precipitation", "Temp Min", "Temp Max"],
	features: [],
	legends: [],
	loading_data: true,
	showSpiral: false,
	guide: [
	    {
		ref: "timeChart",
		text: "Here you can navigate across all the temporal series. <br /> Select a range on the chart to zoom in, use the controls on the top-right side to pan over the chart or to zoom out."
	    },
	    {
		ref: "macroTaskContainer",
		text: "This is the diagram of macroTask you can use. <br /> "
	    },
	    {
		ref: "currentOperation",
		text: "Here you can see the current operation that you choose. First you can open a MacroTask and then select an operator."
	    }
	],
	currentGuide: 0
    }),
    //props: ["dataset", "station", "recommendations"],
    props: [],
    watch: {
	dataset: function (newValue, oldValue) {
	    this.seePresentChart = false;
	    console.log("[ Dataset Name ]:", newValue);
	    console.log("[ Last Dataset Name ]:", oldValue);
	    console.log("[ Dataset Station Name ]:", this.station);
	    axios
		.get(`http://localhost:8080/data/${newValue}/${this.station}`)
		.then(async data => {
		    let raw_data = data.data;
		    await this.disaggregateData(raw_data);
		    console.log("[ Data Station Length ]: ", raw_data.length);
		    if ( this.chart == null) {
			console.log("[ Watch Chart is Null yet ]");
		    } else {
			this.chart.render();
			console.log("[ Watch Chart Rendered ]");
		    }
		    this.history = [];
		})
	},
    },
    methods: {
	async getRecommendations(dataset, station) {
	    let dataOb = await axios.get(`http://localhost:8080/recommendation/${dataset}/${this.titleCase(station)}`)
	    console.log("dataOb", dataOb.data)
	    // let num = "0"
	    let recommends = dataOb.data[0]
	    this.recommendations = recommends
	    this.algorithms = dataOb.data[1]
	    await this.$emit("update:recommendations", this.recommendations);
	    await this.$emit("update:algorithms", this.algorithms);
	    console.log("[ Recommendations ]: ", this.recommendations)
	    console.log("[ Recommended algorithms to fix ]:", this.algorithms.Clean)
	    // this.$refs.macroTaskDiagram.actualizarDiagrama(num);
	    // //this.recommendations = recommendations
	    // //console.log("Recomendatios:", recommendations)
	},
	// newRecommendations(data) {
	//     console.log("[ Additional recommendations ]:", data.recommends)
	//     this.recommendations = data.recommends
	//     console.log("[ Updated recommendations ]:", this.recommendations)
	// },
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
	titleCase(str) {
	    return str.toLowerCase().replace(/\b(\w)/g, s => s.toUpperCase())
	},
	// async showGuide() {
	//     this.currentGuide = 0
	//     this.$refs.guide.open(this.$refs[this.guide[0].ref])
	//     console.log("Text: ", this.$refs[this.guide[0].ref])
	    
	//     const interval = setInterval(async () => {
	// 	console.log(
	// 	    "Guide:",
	// 	    this.currentGuide,
	// 	    this.guide.length,
	// 	    this.$refs[this.guide[this.currentGuide]]
	// 	)
	// 	this.currentGuide += 1
	// 	if (this.currentGuide < this.guide.length) {
	// 	    this.$refs.guide.open(this.$refs[this.guide[this.currentGuide].ref])
	// 	} else {
	// 	    console.log("Finished Interval")
	// 	    clearInterval(interval)
	// 	    this.$refs.guide.close()
	// 	}
	//     }, 3000)
	// },
	async expandPastChart() {
	    this.seePresentChart = false
	    await console.log("The last chart is gonna maximize")
	    this.chart.render()
	},
	viewPorts(e) {
	    console.log(this.chart.options.data[0].dataPoints)
	    console.log(e.chart.axisX[0].minimum)
	},
	async disaggregateData(raw_data) {
	    console.log("[ Raw Data to Split: ]", raw_data, typeof raw_data)
	    if ( typeof raw_data === "string" ) raw_data = JSON.parse(raw_data)
	    // let keys = Object.keys(raw_data[0])
	    if ( this.operation.operation_name === "trend" ||
		 this.operation.operation_name === "seasonality" ||
		 this.operation.operation_name === "cyclicity" ) {
		console.log("[ DISAGGREGATE: TREND, SEASONALITY AND CYCLICITY SECTION ]:", this.operation.operation_name)
		let orig_data = await raw_data.map(el => {
		    return { label: el.date, y: el.orig }
		})
		let result_data = await raw_data.map(el => {
		    return { label: el.date, y: el.result }
		})
		this.legends = ["Source", this.operation.operation_name]
		return [ { datapoints: orig_data },
			 { datapoints: result_data },
			 { datapoints: [] } ]
	    } else /* if (this.operation.operation_name !== "reduce" ||
		       this.operation.operation_name == "reduce") */ {
		console.log("[ DISAGGREGATE: ANY ]:", this.operation.operation_name)
		this.tempMaxData = await raw_data.map (
		    ({ date: label, tempMax: y }) => ({ label, y })
		)
		this.tempMinData = await raw_data.map (
		    ({ date: label, tempMin: y }) => ({ label, y })
		)
		this.precipitationData = await raw_data.map (
		    ({ date: label, precipitation: y }) => ({ label, y })
		)
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
	    } /* else {
		console.log("[ DISAGGREGATE: ELSE, IT WOULD BE NEVER USED ]")
		let feature1 = await raw_data.map(({ date: label, 1: y }) => ({ label, y }))
		let feature2 = await raw_data.map(({ date: label, 2: y }) => ({ label, y }))
		this.legends = ["Component 1", "Component 2"]
		return [
		    { datapoints: feature1 },
		    { datapoints: feature2 },
		    { datapoints: [] }
		]
	    } */
	},
	async rangeChanged(e) {
	    this.chart2AxisX = Object.assign({}, e.axisX[0])
	    console.log("chart", this.chart2AxisX)
	    this.chart1AxisX.viewportMinimum = null
	    this.chart1AxisX.viewportMaximum = null
	    let labels = this.chart.axisX[0].labels
	    let start_pos = Object.keys(labels)[0]
	    let end_pos = Object.keys(labels)[Object.keys(labels).length - 1]
	    console.log(start_pos, end_pos)
	    console.log(labels[start_pos], labels[end_pos])
	    await console.log(
		"Range has changed",
		Object.values(labels)[0],
		labels[labels.length - 1]
	    )
	    this.chart1AxisX.viewportMinimum = Object.values(labels)[0]
	    this.chart1AxisX.viewportMaximum = labels[labels.length - 1]
	},
	async newOperation() {
	    this.loading_data = true
	    console.log("[ Operation ]:", this.operation)
	    console.log("[ Operation Options ]:", this.chart.options)
	    // let viewportMinimum = 0
	    let req_string
	    let string_rec
	    let extra_params = {}
	    if (this.operation.operation_name === "normalize") {
		req_string = `http://localhost:8080/op/${this.dataset}/normalize/${this.operation.method}`
		this.history.push({
		    name: "scale",
		    aux: req_string
		})
	    } else if (this.operation.operation_name === "reduce") {
		req_string = `http://localhost:8080/op/${this.dataset}/reduce/${this.operation.method}/${this.operation.n_comp}`
		this.history.push({
		    name: "reduce",
		    aux: req_string
		})
		// viewportMinimum = null
		// this.reduceSelected = true
	    } else if (this.operation.operation_name === "transform") {
		req_string = `http://localhost:8080/op/${this.dataset}/transform/${this.operation.method}/${this.operation.factor}`
		this.history.push({
		    name: "reduce",
		    aux: req_string
		})
	    } else if (this.operation.operation_name === "clean") {
		req_string = `http://localhost:8080/op/${this.dataset}/clean/${this.operation.method}`
		this.history.push({
		    name: `${this.operation.method}-clean`,
		    aux: req_string
		})
	    } else if (
		this.operation.operation_name === "trend" ||
		    this.operation.operation_name === "seasonality" ||
		    this.operation.operation_name === "cyclicity"
	    ) {
		req_string = `http://localhost:8080/op/${this.dataset}/vbehavior/${this.operation.method}`
		extra_params = {
		    feature: this.operation.feature
		}
		console.log("VBehavior link:", req_string)
		this.history.push({
		    name: `${this.operation.method}-vbehavior`,
		    aux: req_string
		})
		// viewportMinimum = null
		// this.reduceSelected = true
	    } else if (this.operation.operation_name === "raw") {
		console.log("estoy en raw")
		req_string = `http://localhost:8080/op/${this.dataset}/raw`
	    }
	    if (this.operation.operation_name === "clean") {
		console.log("hola estoy en el nuevo clean")
		string_rec = `http://localhost:8080/recommendation/${this.dataset}/${this.station}/0`
		console.log(string_rec)
		this.isClean = true
		this.isCleanFT = true
	    }
	    console.log("Params", extra_params)
	    if (!this.tareasHechas.includes(this.operation.operation_name)) {
		this.tareasHechas.push(this.operation.operation_name)
		console.log("NO INCLUIDO AUN")
	    } else {
		console.log("YA ESTA INCLUIDO")
	    }
	    console.log("TAREAS HECHAS HASTA EL MOMENTO", this.tareasHechas)
	    let raw_data = await axios.get(req_string, { params: extra_params })
	    if (this.isClean && this.isCleanFT) {
		let num = "0"
		let dataOb = await axios.get(string_rec, { params: extra_params })
		console.log("dataOb", dataOb.data)
		let recommends = dataOb.data[0]
		console.log("Recomendaciones antes: ", this.recommendations)
		this.recommendations = recommends
		this.algorithms = dataOb.data[1]
		//await this.$emit("newRec", { recommends })
		await this.$emit("update:recommendations", this.recommendations);
		await this.$emit("update:algorithms", this.algorithms);
		console.log("recomendaciones despues", this.recommendations)
		console.log("Algoritmos recomendados", this.algorithms.Clean)
		this.$refs.macroTaskDiagram.actualizarDiagrama(num);
		if (this.reUpdateMacroTask.length !== 0) {
		    console.log("MACRO TAREAS POR HABILITAR: ", this.reUpdateMacroTask)
		    for (var i = 0; i < this.reUpdateMacroTask.length; i++) {
			document.getElementById(`macro-${this.reUpdateMacroTask[i]}`).classList.add("action")
			document.getElementById(`macro-${this.reUpdateMacroTask[i]}`).classList.add("active")
			this.$refs.macroTaskDiagram.setTasksListeners()
		    }
		} else {
		    console.log("NADA PARA HABILITAR ")
		}
		this.isCleanFT = false
	    }
	    raw_data = raw_data.data
	    // CHART: creating new chart when sep_data is updated
	    console.log("[ Op. Raw Data Length ]:", raw_data.length)
	    const [ interval_start, interval_end ] = this.minmaxInterval(raw_data)
	    // viewportMinimum = interval_start
	    let sep_data = await this.disaggregateData(raw_data)
	    console.log("[ Op. Split Data ]: ", sep_data)
	    console.log("[ Op. Split Data Length ]:", sep_data.length)
	    console.log("[ Op. Interval Chart Values ]: [", interval_start, ",", interval_end, "]")
	    this.chart = new CanvasJS.Chart("graph1", {
		animationEnabled: true,
		exportEnabled: true,
		zoomEnabled: true,
		width: 1072, // commented
		// height: 580,
		axisX: {
		    intervalType: "day"
		},
		axisY: {
		    viewportMinimum: interval_start,
		    viewportMaximum: interval_end
		},
		title: {
		    // text: `Dataset Length: ${this.precipitationData.length}, ${raw_data.length}`
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
	    })
	    console.log("[ Options data ]:", this.chart.options.data)
	    console.log("[ Options Data Length ]:", this.chart.options.data.length)
	    // this.chart.options.axisY.viewportMinimum = this.reduceSelected
	    // 	? null
	    // 	: viewportMinimum
	    this.chart.options.axisX.viewportMinimum = this.chart2AxisX.viewportMinimum
	    this.chart.options.axisX.viewportMaximum = this.chart2AxisX.viewportMaximum
	    console.log("Viendo la fecha inicio fin:",
			sep_data[0].datapoints[0].label,
			sep_data[0].datapoints[sep_data[0].datapoints.length - 1].label
		       )
	    this.chart.render()
	    let id_diagOp = `op-${this.operation.method}`
	    let id_tabOp = `tab-${this.operation.method}`
	    let from_op = document.getElementById(id_diagOp)
	    let to_op = document.getElementById(id_tabOp)
	    console.log("Trying to connect:", id_diagOp, id_tabOp, from_op, to_op)
	    await this.tableIdLines.push({ from: id_diagOp, to: id_tabOp })
	    this.redrawLines()
	    this.loading_data = false
	    console.log("History", this.history)
	},
	doTask(operator) {
	    console.log("doTask", operator.name)
	    this.last_opName = this.main_opName
	    this.last_operation = this.main_operation
	    this.main_opName = operator.name
	    this.main_operation = operator.taskValue
	    this.main_method = operator.value
	    this.infoOperation = operator.name
	    if (this.main_operation === "normalize" ||
		this.main_operation === "clean" ||
		this.main_method === "spiral" ||
		(this.main_operation === "transform" && this.main_method !== "linear") ||
		(this.main_operation === "reduce" && this.main_method !== "manual")) {
		if (this.last_opName) {
		    this.operation.fullName = this.last_opName
		    console.log("Changing operator: ", this.operation)
		    this.pastTable.push(this.operation)
		}
		this.operation = {
		    operation_name: this.main_operation,
		    method: this.main_method,
		    fullName: this.main_opName
		}
		if (this.main_method === "spiral") {
		    this.showSpiral = true
		    this.showSpiralVis()
		    return
		}
		this.showSpiral = false
		this.newOperation()
		return
	    }
	    this.dialog = true
	},
	async redrawLines() {
	    await console.log("Lines before remove", this.tableLines)
	    await this.tableLines.forEach(line => {
		console.log("Removing", line, this.tableLines.length)
		line.remove()
	    })
	    await this.tableLines.splice(0)
	    await console.log("Lines before drawed", this.tableLines)
	    this.linesGravity = 50
	    await this.tableIdLines.forEach(line => {
		let from_op = document.getElementById(line.from)
		let to_op = document.getElementById(line.to)
		// console.log(from_op, to_op)
		const op_line = new LeaderLine(from_op, to_op, {
		    color: "black",
		    startSocket: line.from === "op-raw" ? "bottom" : "top",
		    endSocket: "bottom",
		    hide: false,
		    size: 2.5,
		    path: "fluid"
		    // startSocketGravity: this.linesGravity.valueOf()
		})
		this.linesGravity -= 10
		this.tableLines.push(op_line)
	    })
	    console.log("Lines at the end:", this.tableLines)
	},
	async recMacrotask(macrotaskName) {
	    console.log("Nombre de la Macrotask enviado:", macrotaskName)
	    let request
	    let num = "0"
	    if (this.isClean) {
		this.loading_data = true
		if (macrotaskName == "Data Reduction") {
		    request = `http://localhost:8080/recommendation/${this.dataset}/${this.station}/1`
		    console.log(request)
		    num = "1"
		}
		if (macrotaskName == "Variables Behavior") {
		    request = `http://localhost:8080/recommendation/${this.dataset}/${this.station}/2`
		    console.log(request)
		    num = "2"
		}
		let dataOb = await axios.get(request)
		console.log("dataOb", dataOb.data)
		let recommends = dataOb.data[0]
		//await this.$emit("newRec", { recommends })
		this.recommendations = recommends
		this.algorithms = dataOb.data[1]
		await this.$emit("update:recommendations", this.recommendations);
		await this.$emit("update:algorithms", this.algorithms);
		this.$refs.macroTaskDiagram.actualizarDiagrama(num);
		console.log("diagrama actualizado:", num)
		this.loading_data = false
	    } else {
		console.log("FALTA REALIZAR LIMPIEZA")
		this.loading_data = true
		if (macrotaskName == "Data Reduction") {
		    request = `http://localhost:8080/recommendation/${this.dataset}/${this.station}/1aux`
		    console.log(request)
		    num = "1"
		}
		if (macrotaskName == "Variables Behavior") {
		    request = `http://localhost:8080/recommendation/${this.dataset}/${this.station}/2aux`
		    console.log(request)
		    num = "2"
		}
		let dataOb = await axios.get(request)
		console.log("dataOb", dataOb.data)
		let recommends = dataOb.data[0]
		//await this.$emit("newRec", { recommends })
		this.recommendations = recommends
		this.algorithms = dataOb.data[1]
		await this.$emit("update:recommendations", this.recommendations);
		await this.$emit("update:algorithms", this.algorithms);
		this.$refs.macroTaskDiagram.actualizarDiagrama(num);
		console.log("diagrama actualizado:", num)
		this.loading_data = false
	    }
	},
	selectedTask(taskName) {
	    let cleaned = this.history.find(x => x.name === "clean-knn-clean")
	    //console.log("Looking for cleaned data", this.history, cleaned)
	    console.log("cleaned:", cleaned)
	    console.log("task name:", taskName)
	    if (
		(taskName === "trend" ||
		 taskName == "cyclicity" ||
		 taskName == "seasonality") &&
		    !cleaned
	    ) {
		alert("Select a cleaner first")
		this.reUpdateMacroTask.push(taskName)
		//document.getElementById(`macro-${taskName}`).classList.add("action")
		//document.getElementById(`macro-${taskName}`).classList.add("active")
		//this.$refs.macroTaskDiagram.setTasksListeners()
		return
	    }
	    this.newTask = taskName
	},
	showSpiralVis() {
	    let data = []
	    let points = []
	    let cycles = 5
	    let start_year = 2014
	    for (let index = 0; index < 12 * cycles; index++) {
		var size = Math.floor(Math.random() * 6) + 3
		var mes = index % 12
		var año = parseInt(start_year + index / 12)
		data.push({
		    date: `${año}-${("0" + (mes + 1)).slice(-2)}`,
		    value: size
		})
		points.push([index, size])
	    }
	    var spiral1 = new Spiral("points")
	    console.log("Spiral", spiral1)
	    spiral1.setParam("numberOfPoints", 12 * cycles)
	    spiral1.setParam("period", 12)
	    spiral1.setParam("svgHeight", 680)
	    spiral1.setParam("svgWidth", 650)
	    spiral1.setParam("spacing", 10)
	    spiral1.option.data = points
	    spiral1.option.dates = data
	    spiral1.option.offset = 0
	    spiral1.adjustData()
	    spiral1.render()
	},
	selectedMethod() {
	    console.log("Dialog accept")
	    if (this.main_operation === "reduce" &&
		(this.n_comp === "" || this.n_comp > 3)) {
		this.$refs["n_comp"].validate(true)
		return
	    }
	    if (this.main_operation === "transform" && this.factor === "") {
		this.$refs["factor"].validate(true)
		return
	    }
	    if ((this.main_operation === "seasonality" ||
		 this.main_operation === "trend" ||
		 this.operation.operation_name === "cyclicity") && this.feature === "") {
		this.$refs["feature"].validate(true)
		return
	    }
	    let operation = {
		fullName: this.main_opName,
		operation_name: this.main_operation,
		method: this.main_method,
		n_comp: this.n_comp,
		factor: this.factor,
		feature: this.feature
	    }
	    if (this.last_opName) {
		this.operation.fullName = this.last_opName
		console.log("Changing operator: ", this.operation)
		this.pastTable.push(this.operation)
	    }
	    this.operation = operation
	    this.n_comp = ""
	    this.factor = ""
	    this.feature = ""
	    this.dialog = false
	    this.$refs["parameters_form"].reset()
	    this.newOperation()
	},
	changeVis(item) {
	    console.log("Clicked:", item)
	    let item_idx = this.pastTable.indexOf(item)
	    let displaced_items = this.pastTable.splice(item_idx)
	    displaced_items.push(this.operation)
	    let current_operation = displaced_items.shift()
	    this.futureTable.unshift(...displaced_items)
	    console.log(this.futureTable)
	    console.log("Current operation is:", current_operation)
	    this.operation = item
	    this.infoOperation = current_operation.fullName
	    this.newOperation()
	    console.log("Tables", this.pastTable, this.futureTable)
	    // this.main_opName = this.pastTable.splice(this.pastTable.length - 1)
	},
	changeVisFromFuture(item) {
	    let item_idx = this.futureTable.indexOf(item)
	    let displaced_items = this.futureTable.splice(item_idx)
	    let current_operation = displaced_items.shift()
            ;[this.futureTable, displaced_items] = [displaced_items, this.futureTable]
	    displaced_items.unshift(this.operation)
	    this.pastTable.push(...displaced_items)
	    this.infoOperation = current_operation.fullName
	    this.operation = item
	    this.newOperation()
	}
    },
    mounted: function () {
	this.isClean = false
	this.isCleanFT = false
	this.algorithms = {}
	this.dataset = this.$route.params.dataset
	this.station = this.$route.params.station
	document.getElementById("dynNet").href=`/net/${this.dataset}/${this.station}`;
	document.getElementById("dynVisualize").href=`/visualize/${this.dataset}/${this.station}`;
	document.getElementById("dynStats").href=`/stats/${this.dataset}/${this.station}`;
	document.getElementById("dynSpiral").href=`/spiral/${this.dataset}/${this.station}`;
	// this.getRecommendations(this.dataset, this.station)
	console.log("[ Time Series ]", this.dataset, this.station, this.recommendations)
	axios
	    .get(`http://localhost:8080/data/${this.dataset}/${this.station}`)
	    .then(async data => {
		let raw_data = data.data
		// CHART: creating new chart with disaggregated sep_data
		console.log("[ Mounted Raw Data Length ]:", raw_data.length)
		const [ interval_start, interval_end ] = this.minmaxInterval(raw_data)
		let sep_data = await this.disaggregateData(raw_data)
		console.log("[ Mounted Split Data ]: ", sep_data)
		console.log("[ Mounted Split Data Length ]:", sep_data.length)
		console.log("[ Mounted Interval Chart Values ]: [", interval_start, ",", interval_end, "]")
		this.chart = new CanvasJS.Chart("graph1", {
		    animationEnabled: true,
		    exportEnabled: true,
		    zoomEnabled: true,
		    width: 1072, // commented
		    // height: 580,
		    axisX: {
			intervalType: "day"
		    },
		    axisY: {
			viewportMinimum: interval_start,
			viewportMaximum: interval_end
		    },
		    title: {
			// text: `Dataset Length: ${this.precipitationData.length}, ${raw_data.length}`
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
		})
		this.chart.render()
		this.loading_data = false
	    })
	this.operation = {
	    fullName: "Raw Data",
	    operation_name: "raw",
	    method: "raw"
	}
	console.log("Time series re:", this.recommendations)
	this.main_opName = "Raw Data"
	this.main_operation = "raw"
	this.tareasHechas = []
	console.log("Start:", this.$refs.timeChart)
	// this.showGuide()
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
table.pastTable {
    margin-left: auto;
}
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
</style>
