<template>
  <div class="diagram-container">
    <div class="test" id="taskDiagram" ref="diagram"></div>
  </div>
</template>

<script>
import { render as Renderer } from "dagre-d3"
import { Graph } from "graphlib"
import { select } from "d3-selection"
export default {
    data() {
	return {
	    dagreChart: new Graph(),
	    macroTaskStages: [[0], [1], [2, 3, 5]],
	    macroTasks: [
		{
		    taskName: "Quality of Data",
		    tasks: [
			{
			    name: "Clean",
			    value: "clean",
			    description: "This action is recommended for these reasons:",
			    active: true,
			    bgColor: "fdca40",
			    required: true
			},
			{
			    name: "Normalize",
			    value: "normalize",
			    description: "This action is recommended for these reasons:",
			    active: true,
			    bgColor: "94bfa7",
			    required: false
			},
			{
			    name: "Transform",
			    value: "transform",
			    description: "This action is recommended for these reasons:",
			    active: true,
			    bgColor: "e0b7b7",
			    required: false
			}
		    ],
		    bgColor: "94bfa7"
		},
		{
		    taskName: "Data reduction",
		    tasks: [
			{
			    name: "Dim.Reduce",
			    value: "reduce",
			    description: "This action is recommended for these reasons:",
			    active: true,
			    bgColor: "f7a1c4",
			    required: false
			},
			{
			    name: "Data Sampling",
			    value: "sampling",
			    required: false,
			    active: true,
			    notYet: true
			},
			{
			    name: "Feat. Selection",
			    value: "selection",
			    required: false,
			    active: true,
			    notYet: true
			}
		    ],
		    bgColor: "e0b7b7"
		},
		{
		    taskName: "Variables Behavior",
		    tasks: [
			{ name: "Trend", value: "trend", active: true, required: false },
			{
			    name: "Cyclicity",
			    value: "cyclicity",
			    description: "This action is recommended for these reasons:",
			    active: true,
			    required: false
			},
			{
			    name: "Seasonality",
			    value: "seasonality",
			    description: "This action is recommended for these reasons:",
			    active: true,
			    required: false
			}
		    ]
		},
		{
		    taskName: "Temporal Features",
		    tasks: [
			{
			    name: "Data distribution",
			    value: "distribution",
			    required: false,
			    active: true,
			    notYet: true
			},
			{
			    name: "Patterns",
			    value: "patterns",
			    required: false,
			    active: true,
			    notYet: true
			},
			{
			    name: "Anomalies",
			    value: "anomalies",
			    required: false,
			    active: true,
			    notYet: true
			}
		    ],
		    bgColor: "ffe347",
		    disabled: true
		},
		{
		    taskName: "Data Redudancy",
		    disabled: true
		},
		{
		    taskName: "Data with similar behavior ",
		    disabled: true
		},
		{
		    taskName: "Analize stadistic behavior",
		    disabled: true
		}
	    ],
	    arrow: `<i class="arrow right">`,
	    nextTask: 0,
	    nextStage: 0
	}
    },
    created: async function () {
	console.log("Re:", this.recommendations)
	this.dagreChart.setGraph({
	    rankdir: "LR",
	    nodesep: 10
	})
	// dagre flow chart

	let currentMacroTask = this.macroTasks[this.nextTask]
	console.log("nextTask1", this.nextTask)
	let isRecommended = currentMacroTask.taskName in this.recommendations
	this.dagreChart.setNode("0", {
	    // label: "Quality of Data " + this.arrow,
	    label: this.getBlockHtml(currentMacroTask),
	    labelType: "html",
	    style: isRecommended ? "stroke: rgba(255, 0, 0, 0.808)" : ""
	})

	this.nextTask += 1
	this.nextStage += 1
	console.log("nextTask2", this.nextTask)
    },

    components: {},
    props: ["dataset", "station", "recommendations", "algorithms"],
    mounted: async function () {
	console.log(
	    "Diagram props",
	    this.dataset,
	    this.station,
	    this.recommendations,
	    this.algorithms
	)
	//this.$on("ejecutarMetodo", this.actualizarDiagrama);
	const ref = this.$refs.diagram
	await this.render(ref)
	this.setNodeBounds()
	this.setNodeSettings(ref)
	this.setTasksListeners(ref)
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
		.attr("height", "26vh")
		.attr("overflow", "scroll")
	    const svgGroup = svg.append("g")
	    const renderer = new Renderer()
	    console.log("Chart:", this.dagreChart)
	    renderer(svgGroup, this.dagreChart)
	},
	actualizarDiagrama(mt) {
	    console.log("number mt:", mt)
	    let currentMacroTask = this.macroTasks[mt]
	    console.log("currentMacroTask es:", currentMacroTask)
	    console.log("recomendaciones actual:", this.recommendations)
	    console.log("Algoritmos en diagram", this.algorithms)
	    let isRecommended = currentMacroTask.taskName in this.recommendations
	    this.dagreChart.setNode(mt, {
		// label: "Quality of Data " + this.arrow,
		label: this.getBlockHtml(currentMacroTask),
		labelType: "html",
		style: isRecommended ? "stroke: rgba(255, 0, 0, 0.808)" : ""
	    })
	    const ref = this.$refs.diagram

	    this.setNodeBounds()
	    this.render(ref)
	    this.setNodeSettings(ref)
	    this.setTasksListeners(ref)
	    this.setMacroTasksElectionListeners(ref)
	},
	addEdge(e) {
	    console.log(this.macroTasks)
	    if (this.macroTasks.length <= this.nextTask) return
	    const ref = this.$refs.diagram

	    let lastTaskId = this.macroTaskStages[this.nextStage - 1][0]
	    let newTaskId = this.macroTaskStages[this.nextStage][0]
	    console.log(
		"MacroTaskClicked: ",
		e.target,
		lastTaskId,
		newTaskId,
		this.nextStage
	    )

	    if (this.macroTaskStages[this.nextStage].length > 1) {
		let currentMacroTasks = []
		this.macroTaskStages[this.nextStage].forEach(i => {
		    let macroTask = this.macroTasks[i]
		    currentMacroTasks.push(macroTask.taskName)
		    let labelTemplate = `
            <table>
              <td style="vertical-align:middle;"
              class="border taskName ${macroTask.disabled ? "disabled" : "toChoose"
            }"
              data-id="${i}">
                ${macroTask.taskName}
              </td>
            </table>`
		    this.dagreChart.setNode(i, {
			label: labelTemplate,
			labelType: "html"
		    })
		    let color_arrow = macroTask.disabled ? "#000" : "#f66"
		    this.dagreChart.setEdge(lastTaskId, i, {
			label: "",
			style: `stroke: ${color_arrow};`,
			arrowheadStyle: `fill: ${color_arrow};`
		    })
		})
		console.log("Stage macroTasks:", currentMacroTasks)
	    } else {
		let currentMacroTask = this.macroTasks[newTaskId]
		console.log("New MacroTask: ", currentMacroTask)
		console.log("Macrotarea: ", currentMacroTask.taskName)
		this.$emit("macrotaskRec", currentMacroTask.taskName)

		console.log("Last MacroTask: ", this.macroTasks[lastTaskId])

		let isRecommended = currentMacroTask.taskName in this.recommendations
		this.dagreChart.setNode(newTaskId, {
		    label: this.getBlockHtml(currentMacroTask),
		    labelType: "html",
		    style: isRecommended ? "stroke: rgba(255, 0, 0, 0.808)" : ""
		})
		this.dagreChart.setEdge(lastTaskId, newTaskId, {
		    label: "",
		    style: `stroke: #f66;`,
		    arrowheadStyle: `fill: #f66;`
		})
		this.nextStage += 1

		// this.nextTask += 1
	    }

	    this.setNodeBounds()
	    this.render(ref)
	    this.setNodeSettings(ref)
	    this.setTasksListeners(ref)
	    this.setMacroTasksElectionListeners(ref)
	},
	taskClick(e) {
	    console.log("Task clicked", e.target, e.target.dataset.value, e)

	    e.target.classList.remove("action")
	    e.target.classList.remove("active")

	    e.target.classList.remove("icon-inactive")
	    // e.target.style = ""
	    e.target.removeEventListener("click", this.taskClick)
	    let macroTaskIdx = this.macroTasks.findIndex(
		macroTask => macroTask.taskName === e.target.dataset.macrotask
	    )

	    let taskIdx = this.macroTasks[macroTaskIdx].tasks.findIndex(
		task => task.name === e.target.innerText
	    )

	    this.macroTasks[macroTaskIdx].tasks[taskIdx].active = false
	    this.macroTasks[macroTaskIdx].tasks[taskIdx].used = true

	    if (this.macroTasks[macroTaskIdx].tasks[taskIdx].notYet) {
		alert("Macro Task not implemented yet")
		e.target.classList.add("icon-inactive")

		return
	    }

	    this.dagreChart.node(macroTaskIdx).label = this.getBlockHtml(
		this.macroTasks[macroTaskIdx]
	    )
	    console.log("viendo macroTaskIdx:", macroTaskIdx)
	    console.log("viendo el getBlockHtml:", this.macroTasks[macroTaskIdx])

	    const ref = this.$refs.diagram

	    this.setNodeBounds()
	    this.render(ref)
	    this.setNodeSettings(ref)
	    this.setTasksListeners(ref)
	    this.setMacroTasksElectionListeners(ref)

	    this.$emit("taskSelected", e.target.dataset.value)
	},
	removeFromArray(arr, value) {
	    var index = arr.indexOf(value)
	    if (index > -1) {
		arr.splice(index, 1)
	    }
	},
	macroTaskChoosed(e) {
	    console.log("Task:", e.target.innerText, e.target.dataset.id)
	    let currentStageIds = this.macroTaskStages[this.nextStage]
	    console.log("Current Stage", currentStageIds, this.nextStage)
	    for (let index = 0; index < currentStageIds.length; index++) {
		this.dagreChart.removeNode(currentStageIds[index])
	    }

	    let choosedMacroTaskId = parseInt(e.target.dataset.id)

	    this.removeFromArray(
		this.macroTaskStages[this.nextStage],
		choosedMacroTaskId
	    )

	    this.macroTaskStages.splice(this.macroTaskStages.length - 1, 0, [
		choosedMacroTaskId
	    ])
	    console.log("Current Stage", this.macroTaskStages, this.nextStage)
	    this.addEdge(e)
	},
	getBlockHtml(macroTask) {
	    let taskName = macroTask.taskName
	    let actions = macroTask.tasks

	    let isRecommended = taskName in this.recommendations
	    if (isRecommended) {
		actions.forEach(action => {
		    console.log(
			"Block HTML: ",
			action.name,
			this.recommendations[taskName]
		    )
		    if (this.recommendations[taskName].includes(action.name)) {
			console.log("Found")
			action.required = true
		    } else {
			action.required = false
		    }
		})
	    }
	    // <span class="mdi mdi-name"></span>
	    // <span ><i class=""></i></span>
	    console.log("blockHTML", this.recommendations, taskName, isRecommended)
	    let template = `
	    <table class="macroTask">
	      <tr>
	        ${actions
	        .map(
	        action =>
	        `<td id="macro-${action.value}" class="border icon-inactive ${action.active ? "action active" : "" } ${action.required ? "required" : ""}"
	    	     data-value="${action.value}" data-macroTask="${taskName}" ${action.active ? `style="background-color: #${action.bgColor}` : "" }"
	    	     title="${action.description}
	    		    ${action.name === "Clean" ? this.algorithms.Clean :
	    		      action.name === "Normalize" ? this.algorithms.Normalize :
	    		      action.name === "Transform" ? this.algorithms.Transform :
	    	              action.name === "Dim.Reduce" ? this.algorithms.DimRed :
	    		      action.name === "Cyclicity" ? this.algorithms.Cyclicity :
	    	              action.name === "Seasonality" ? this.algorithms.Seasonality : ""}">
	          ${action.name}
	          <span class="mdi mdi-check-circle-outline check-icon"></span>
	        </td>`
	        )
	        .join(" ")}
	        <td rowspan = "2"><span" class="mdi mdi-arrow-right-drop-circle-outline arrow"></span></td>
	    </tr>
	    <tr>
	      <td colspan="${actions.length}" style="vertical-align:middle;" class="border taskName" >${taskName}</td>
	    </tr>
	    </table>`
	    return template
	},
	setNodeBounds() {
	    this.dagreChart.nodes().forEach(v => {
		let node = this.dagreChart.node(v)
		node.rx = node.ry = 5
	    })
	},
	setNodeSettings(ref) {
	    let nodes = ref.getElementsByClassName("arrow")
	    nodes[nodes.length - 1].addEventListener("click", this.addEdge)

	},
	setTasksListeners(ref) {
	    if (!ref) {
		ref = this.$refs.diagram
	    }
	    let tasks = ref.getElementsByClassName("action active")
	    for (let i = 0; i < tasks.length; i++) {
		const element = tasks[i]
		element.addEventListener("click", this.taskClick)
	    }
	},
	setMacroTasksElectionListeners(ref) {
	    let macroTasks = ref.getElementsByClassName("taskName toChoose")
	    for (let i = 0; i < macroTasks.length; i++) {
		const element = macroTasks[i]
		element.addEventListener("click", this.macroTaskChoosed)
	    }
	}
    }
}
</script>

<style>
/* #app { */
/*     font-family: "Avenir", Helvetica, Arial, sans-serif; */
/*     -webkit-font-smoothing: antialiased; */
/*     -moz-osx-font-smoothing: grayscale; */
/*     text-align: center; */
/*     color: #2c3e50; */
/*     margin-top: 60px; */
/* } */
.test .node rect,
.test .node circle,
.test .node ellipse,
.test .node polygon {
    stroke: #333;
    fill: #fff;
    stroke-width: 1.5px;
}
.test .edgePath path {
    stroke: #333;
    fill: #333;
    stroke-width: 1.5px;
}
.arrow {
    /* border: solid green; */
    /* border-width: 0 3px 3px 0; */
    display: block;
    padding: 3px;
    cursor: pointer;
    color: green;
    font-size: x-large;
}
.right {
    transform: rotate(-45deg);
    -webkit-transform: rotate(-45deg);
}
td[colspan="3"] {
    text-align: center;
}
td.border {
    border: 1px solid black;
    border-collapse: collapse;
    border-spacing: 0;
    border-radius: 5px;
}
i.within {
    position: absolute;
    right: 5px;
    top: 5px;
}
table.macroTask {
    position: relative;
}
table.macroTask.recomended {
    background-color: rgb(51, 51, 172);
}
@media (max-width: 1200px) {
    table.macroTask {
	font-size: 0.9em;
	/* 19px */
    }
    /**
     * El font-size del resto de elementos
     * se actualizará automáticamente
     */
}
td.used {
    position: relative;
}
td.action.active {
    background-color: rgba(148, 149, 153, 0.3) !important;
    cursor: pointer;
}
td.title {
    column-gap: 20px;
    font-size: 14px;
    line-height: 1.5;
}
td.action.active:hover {
    filter: brightness(110%);
}
td.task.show-info {
    cursor: pointer;
}
td.task.show-info:hover {
    filter: brightness(110%);
}
td.taskName {
    background-color: rgba(255, 136, 0, 0.3);
}
td.taskName.toChoose {
    background-color: rgba(212, 29, 16, 0.3);
    border: 2px solid rgba(255, 0, 0, 0.808);
    cursor: pointer;
}
td.taskName.disabled {
    background-color: white;
}
tr>td {
    padding-right: 3px;
    padding-left: 3px;
}
.check-icon {
    float: right;
    color: green;
    display: block;
}
.icon-inactive>span {
    display: none !important;
}
td.action.active.required {
    border: 2px solid rgba(255, 0, 0, 0.808);
    background-color: rgba(212, 29, 16, 0.3) !important;
}
td.required {
    border: 2px solid rgba(255, 0, 0, 0.808);
    background-color: rgba(212, 29, 16, 0.3) !important;
}
.edgePath path.path {
    stroke: #333;
    fill: none;
    stroke-width: 1.5px;
}
</style>
