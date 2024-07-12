<template>
  <div class="diagram-container fill-height">
    <!-- <div class="text-h6">
	 Operation: {{ this.infoOperation ? this.infoOperation : "No Selected" }}
	 </div> -->
    <div class="test pl-4 fill-height" id="operatorDiagram" ref="diagram"></div>
    <v-dialog v-model="openInfo" width="60%">
      <v-card v-if="selectedInfo">
        <v-card-title class="text-h5 grey lighten-2">
          {{ selectedInfo }}
        </v-card-title>
        <v-card-text class="text-body-1">
          <br />
          <div v-html="infoJson[selectedInfo].text"></div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="openInfo = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { render as Renderer } from "dagre-d3"
import { Graph } from "graphlib"
import { select } from "d3-selection"
import LeaderLine from "leader-line-new"
// import tippy from "tippy.js"
// import "tippy.js/dist/tippy.css" // optional for styling
import info_json from "./operators_info.json"
export default {
    props: ["newTask", "recommendations"],
    data() {
	return {
	    dagreChart: new Graph(),
	    macroTaskStages: [[0], [1], [2, 3, 5]],
	    tasks: [
		{
		    taskName: "Clean",
		    operators: [
			{ name: "Rolling Mean/Median Padding", value: "rm", active: true },
			{ name: "Decision Tree Padding", value: "dtr", active: true },
			{ name: "Stochastic Gradient Boosting Padding", value: "sgb", active: true },
			{ name: "Locally Weighted Regression Padding", value: "lwr", active: true },
			{ name: "Legendre Polynomials Padding", value: "lgd", active: true },
			{ name: "Random Forest Regressor Padding", value: "rfr", active: true },
			{ name: "KNN Padding", value: "knn", active: true }
		    ],
		    taskValue: "clean",
		    required: true
		},
		{
		    taskName: "Normalize",
		    operators: [
			{ name: "MinMax Scaler", value: "minmax", active: true },
			{ name: "Standard Scaler", value: "standard", active: true },
			{ name: "MaxAbs Scaler", value: "maxabs", active: true },
			{ name: "Robust Scaler", value: "robust", active: true }
		    ],
		    taskValue: "normalize",
		    bgColor: "94bfa7"
		},
		{
		    taskName: "Transform",
		    operators: [
			{ name: "Linear Transform", value: "linear", active: true },
			{ name: "Quadratic Transform", value: "quadratic", active: true },
			{ name: "Square Root Transform", value: "sqrt", active: true },
			{ name: "Logarithm Transform", value: "log", active: true },
			{ name: "Differencing Transform", value: "diff", active: true }
		    ],
		    taskValue: "transform",
		    bgColor: "e0b7b7"
		},
		{
		    taskName: "Dim.Reduce",
		    operators: [
			{ name: "Factor Analysis (FA)", value: "factor", active: true },
			{ name: "Features Manually Selected", value: "manual", active: true }
		    ],
		    taskValue: "reduce",
		    bgColor: "f7a1c4"
		},
		{
		    taskName: "Trend",
		    operators: [
			{ name: "Trend operator", value: "trend", active: true }
		    ],
		    taskValue: "trend",
		    bgColor: "6494ed4d",
		    required: true
		},
		{
		    taskName: "Seasonality",
		    operators: [
			{ name: "Seasonality operator", value: "seasonality", active: true }
		    ],
		    taskValue: "seasonality",
		    bgColor: "6494ed4d",
		    required: true
		},
		{
		    taskName: "Cyclicity",
		    operators: [
			{ name: "Cyclicity operator", value: "cyclicity", active: true },
			{ name: "Spiral Visualization", value: "spiral", active: true }
		    ],
		    taskValue: "cyclicity",
		    bgColor: "6494ed4d",
		    required: true
		}
	    ],
	    nextId: 0,
	    nextTask: 0,
	    infoOperation: "",
	    lineOptions: {
		color: "black",
		startSocket: "top",
		endSocket: "bottom",
		hide: true,
		size: 2.5,
		startSocketGravity: 80
	    },
	    openInfo: false,
	    infoJson: info_json,
	    selectedInfo: ""
	}
    },
    watch: {
	newTask(newValue) {
	    let newTaskObj = this.tasks.find(task => task.taskValue === newValue)
	    console.log("New operator: ", newTaskObj)
	    this.dagreChart.setNode(this.nextId, {
		label: this.getBlockHtml(newTaskObj),
		labelType: "html"
	    })

	    if (this.nextId >= 1) {
		this.dagreChart.setEdge(this.nextId - 1, this.nextId, {
		    label: ""
		})
	    }
	    this.nextId += 1

	    const ref = this.$refs.diagram
	    this.setNodeBounds()

	    this.render(ref)
	    this.setTasksListeners(ref)
	    this.setInfoListeners(ref)

	    let from_block = document.getElementById(`macro-${newTaskObj.taskValue}`)
	    let to_block = document.getElementById(`task-${newTaskObj.taskValue}`)

	    console.log(
		"trying to connect",
		from_block,
		to_block,
		newTaskObj.taskValue
	    )
	    this.lineOptions.color = newTaskObj.required ? "red" : "black"
	    const line = new LeaderLine(from_block, to_block, this.lineOptions)
	    line.show("draw", { duration: 400, timing: "ease" })

	    // document.getElementsByClassName("operator").forEach(ele => {
	    // 	tippy(ele, {
	    // 	    content: ele.dataset.opname
	    // 	})
	    // })
	}
    },
    created: function () {
	this.dagreChart.setGraph({
	    rankdir: "LR",
	    nodesep: 10
	})
    },

    components: {},
    mounted: function () {
	const ref = this.$refs.diagram
	this.setNodeBounds()

	this.render(ref)
	this.setTasksListeners(ref)
	this.setInfoListeners(ref)
    },
    methods: {
	async render(root) {
	    let svg = select(root)

	    svg.selectAll("*").remove()
	    svg = select(root)
		.append("svg")
		.attr("id", "f" + root.id)
		.attr("xmlns", "http://www.w3.org/2000/svg")
		.attr("width", "100%")
		.attr("height", "100%")
	    const svgGroup = svg.append("g")
	    const renderer = new Renderer()
	    await renderer(svgGroup, this.dagreChart)
	    this.$emit("rendered")
	},
	operatorClick(e) {
	    console.log("Operator clicked", e.target, e.target.dataset.value)

	    this.$emit("operatorSelected", {
		name: e.target.dataset.opname,
		value: e.target.dataset.value,
		taskValue: e.target.dataset.taskvalue
	    })
	    this.infoOperation = e.target.dataset.opname
	},
	showInfo(e) {
	    this.openInfo = true
	    console.log(e.target)
	    this.selectedInfo = e.target.outerText
	},
	setNodeBounds() {
	    this.dagreChart.nodes().forEach(v => {
		let node = this.dagreChart.node(v)
		node.rx = node.ry = 5
	    })
	},
	setTasksListeners(ref) {
	    let tasks = ref.getElementsByClassName("operator active")
	    for (let i = 0; i < tasks.length; i++) {
		const element = tasks[i]
		element.addEventListener("click", this.operatorClick)
	    }
	},
	setInfoListeners(ref) {
	    let tasks = ref.getElementsByClassName("task show-info")
	    console.log("Info listen: ", tasks)
	    for (let i = 0; i < tasks.length; i++) {
		const element = tasks[i]
		element.addEventListener("click", this.showInfo)
	    }
	},
	getBlockHtml(task) {
	    let taskName = task.taskName
	    let actions = task.operators
	    let bgColor = task.bgColor
	    console.log("Block:", task)
	    let template = `
                <table class="taskTable">
                  <tr>
                    ${actions.map((action, idx) => `<td id="op-${action.value}" class="border operator ${action.active ? "active" : ""}" data-value="${action.value}" data-taskvalue="${task.taskValue}" data-opname="${action.name}" title="${action.name}">${idx + 1}</td>`).join(" ")}
                  </tr>
                  <tr>
                    <td id="task-${task.taskValue}" colspan="${actions.length}" style="vertical-align:middle; background-color: #${bgColor};" class="border task show-info">${taskName}</td>
                  </tr>
                </table>`
            return template
	}
    }
}
</script>

<style>
td.operator.active {
    background-color: rgba(24, 202, 8, 0.623);
    cursor: pointer;
}
td.operator.active:hover {
    filter: brightness(140%);
}
td.task {
    background-color: rgba(17, 0, 255, 0.3);
}
table.taskTable {
    width: 100px;
}
/* .tippy-content { */
/*     font-family: "Nunito", sans-serif !important; */
/* } */
</style>
