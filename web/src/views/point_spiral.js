const d3 = require("d3")
const legends = require("d3-svg-legend")

function Spiral(graphType) {
    this.option = {
	graphType: graphType || "points",
	numberOfPoints: null,
	period: null,
	margin: {
	    top: 10,
	    right: 10,
	    bottom: 10,
	    left: 30
	},
	svgHeight: 0,
	svgWidth: 0,
	spacing: 1,
	lineWidth: 50,
	targetElement: "#chart",
	data: [],
	x: d3
	    .scaleLinear()
	    .range([0, 730])
	    .domain([-750, 750]),
	y: d3
	    .scaleLinear()
	    .range([480, 0])
	    .domain([-500, 500]),
	tickMarkNumber: [],
	tickMarkLabels: [],
	color: "black",
	colorMode: "opacity",
	radiusParam: 150
    }
}

Spiral.prototype.cartesian = function(radius, angle, size) {
    var classObj = this
    var option = classObj.option
    size = size || 1
    var xPos = option.x(radius * -Math.cos(angle))
    var yPos = option.y(radius * Math.sin(angle))
    return [xPos, yPos, size]
}

Spiral.prototype.adjustData = function() {
    let classObj = this
    let option = classObj.option
    let temp_data = []
    for (let index = 0; index < option.data.length; index++) {
	var angle = theta(index, option.period, option.offset)
	var rad = radius(option.spacing, angle)
	var size = option.data[index][1]
	temp_data.push(this.cartesian(rad, angle, size))
    }
    option.data = temp_data
}

Spiral.prototype.render = function() {
    var classObj = this
    var option = classObj.option
    let min = d3.min(option.data, d => d[2])
    let max = d3.max(option.data, d => d[2])
    let colorScale = d3
	.scaleLinear()
	.domain([min, max])
	.range(["#fff33b", "#e93e3a"])
    console.log("Rendering Spiral", option.data)
    let scalar = legends
	.legendColor()
	.cells(10)
	.shapeWidth(50)
	.orient("horizontal")
	.scale(colorScale)
    d3.select("#chart-legend")
	.append("svg")
	.attr("width", option.svgWidth)
	.attr("height", "40")
	.append("g")
	.attr("transform", "translate(" + (option.margin.left + 40) + "," + 0 + ")")
	.attr("class", "legendLinear")
	.call(scalar)
    var svg = d3
	.select(option.targetElement)
	.append("svg")
	.attr("width", option.svgWidth)
	.attr("height", option.svgHeight)
	.attr("viewBox", "-100 -200 1000 1000")
    var end
    option.data.forEach(function(datum, t) {
	var start = startAngle(t, option.period, option.offset)
	end = endAngle(t, option.period, option.offset)
	var startCenter = radius(option.spacing, start, option.radiusParam)
	var endCenter = radius(option.spacing, end, option.radiusParam)
	var startInnerRadius = startCenter - option.lineWidth * 0.5
	var startOuterRadius = startCenter + option.lineWidth * 0.5
	var endInnerRadius = endCenter - option.lineWidth * 0.5
	var endOuterRadius = endCenter + option.lineWidth * 0.5
	var ctrlInnerRad = 0.01
	var ctrlOuterRad = 0.01
	var angle = theta(t, option.period, option.offset)
	var rad = radius(option.spacing, angle, option.radiusParam)
	var innerControlPoint = classObj.cartesian(
	    rad - option.lineWidth * 0.5 + ctrlInnerRad,
	    angle
	)
	var outerControlPoint = classObj.cartesian(
	    rad + option.lineWidth * 0.5 + ctrlOuterRad,
	    angle
	)
	var startPoint = classObj.cartesian(startInnerRadius, start)
	var point2 = classObj.cartesian(startOuterRadius, start)
	var point3 = classObj.cartesian(endOuterRadius, end)
	var point4 = classObj.cartesian(endInnerRadius, end)
	datum[1] =
	    "M" + startPoint[0] + " " + startPoint[1] +
	    "L" + point2[0] + " " + point2[1] +
	    "Q" + outerControlPoint[0] + " " + outerControlPoint[1] +
	    " " + point3[0] + " " + point3[1] +
	    "L" + point4[0] + " " + point4[1] +
	    "Q" + innerControlPoint[0] + " " + innerControlPoint[1] +
	    " " + startPoint[0] + " " + startPoint[1] + "Z"
    })
    svg
	.append("g")
	.attr(
	    "transform",
	    "translate(" + option.margin.left + "," + option.margin.top + ")"
	)
    svg
	.selectAll("g")
	.selectAll("path")
	.data(option.data)
	.enter()
	.append("path")
	.style("opacity", "0")
	.attr("fill", function(d) {
	    return colorScale(d[2])
	})
	.attr("d", function(d) {
	    return d[1]
	})
	.on("mouseover", function(values, idx) {
	    let comp_idx = idx % option.period
	    let circles = this.parentElement.children
	    while (comp_idx < option.data.length) {
		circles[comp_idx].setAttribute("stroke", "black")
		circles[comp_idx].setAttribute("stroke-width", "1")
		comp_idx += option.period
	    }
	    option.hoverFunction(values, idx)
	})
	.on("mouseout", function(v, idx) {
	    let comp_idx = idx % option.period
	    let circles = this.parentElement.children
	    while (comp_idx < option.data.length) {
		circles[comp_idx].setAttribute("stroke", "none")
		comp_idx += option.period
	    }
	})
	.append("svg:title")
	.text((d, i) => {
	    // console.log("owo:", i, d)
	    return `${option.dates[i].date}`
	})
    // animate SVG
    svg
	.selectAll("path")
	.transition()
	.delay(function(d, i) {
	    return i * 2
	})
	.duration(10)
	.style("opacity", "1")
    // Labels
    var id = d3.selectAll(".love-spiral")._groups.length
    var segmentLabels = [
	"December",
	"November",
	"October",
	"September",
	"August",
	"July",
	"June",
	"May",
	"April",
	"March",
	"February",
	"January"
    ]
    segmentLabels = [...Array(option.period).keys()]
    console.log(segmentLabels)
    var r = 50
    var labels = svg
	.append("g")
	.classed("labels", true)
	.classed("segment", true)
	.attr(
	    "transform",
	    `translate(${option.svgWidth / 2 + 10},${option.svgHeight / 2})`
	)
    labels
	.append("def")
	.append("path")
	.attr("id", "segment-label-path-" + id)
	.attr("d", "m0 -" + r + " a" + r + " " + r + " 0 1 1 -1 0")
    labels
	.selectAll("text")
	.data(segmentLabels)
	.enter()
	.append("text")
	.append("textPath")
	.attr("xlink:href", "#segment-label-path-" + id)
	.attr("startOffset", function(d, i) {
	    return (i * 100) / option.period + "%"
	})
	.text(function() {
	    return "|"
	    // let month = segmentLabels.indexOf(d) + 1
	    // return ("0" + month).slice(-2)
	})
}

Spiral.prototype.randomData = function() {
    var classObj = this
    var option = classObj.option
    option.data = []
    for (var i = 0; i < option.numberOfPoints; i++) {
	var angle = theta(i, option.period, option.offset)
	var rad = radius(option.spacing, angle)
	var size = 1 + Math.random() * 1.5
	if (i % 10 === 0) {
	    size = 1.5 + Math.random() * 3
	}
	if (option.graphType === "non-spiral") {
	    option.data.push([i, size * option.period, 2])
	} else {
	    option.data.push(this.cartesian(rad, angle, size))
	}
    }
}

Spiral.prototype.setParam = function(param, value) {
    var classObj = this
    var option = classObj.option
    option[param] = value
    if (
	[
	    "svgHeight",
	    "svgWidth",
	    "margin.top",
	    "margin.right",
	    "margin.bottom",
	    "margin.left"
	].indexOf(param) > -1
    ) {
	var width = option.svgWidth - option.margin.left - option.margin.right
	var height = option.svgHeight - option.margin.top - option.margin.bottom
	option.x = d3
	    .scaleLinear()
	    .range([0, width])
	    .domain([-option.svgWidth, option.svgWidth])
	option.y = d3
	    .scaleLinear()
	    .range([height, 0])
	    .domain([-option.svgHeight, option.svgHeight])
    }
}

Spiral.prototype.redraw = function() {
    var classObj = this
    var option = classObj.option
    var graphContainer = document.getElementById(option.targetElement.substr(1))
    var legendContainer = document.getElementById("chart-legend")
    while (graphContainer.firstChild) {
	graphContainer.removeChild(graphContainer.firstChild)
    }
    while (legendContainer.firstChild) {
	legendContainer.removeChild(legendContainer.firstChild)
    }
    classObj.render()
}

Spiral.prototype.autocorrelate = function() {
    var n = this.option.numberOfPoints
    var index = this.option.graphType === "non-spiral" ? 1 : 2
    var sum = 0
    for (var i = 0; i < n; i++) {
	sum += this.option.data[i][index]
    }
    var avg = sum / n
    var sigma2 = 0
    for (let j = 0; j < n; j++) {
	sigma2 += Math.pow(this.option.data[j][index] - avg, 2)
    }
    var coeff
    var coeffArray = []
    for (var tau = 0; tau < n; tau++) {
	var sigma1 = 0
	for (let j = 0; j < n - tau; j++) {
	    sigma1 +=
		(this.option.data[j][index] - avg) *
		(this.option.data[j + tau][index] - avg)
	}

	coeff = sigma1 / sigma2
	coeffArray.push([tau, coeff])
    }
    return coeffArray
}

Spiral.prototype.findPeriod = function() {
    var averageCoeff = 0
    var coeffStdDev = 0
    var coeffDiffSum = 0
    var coeffArray = this.autocorrelate()
    var tauArray = []
    var potentialPeriods = {}
    var periodOccurance = 1
    var foundPeriod = 1
    for (let i = 0; i < coeffArray.length; i++) {
	averageCoeff += coeffArray[i][1]
    }
    averageCoeff = averageCoeff / coeffArray.length
    for (let i = 0; i < coeffArray.length; i++) {
	coeffDiffSum += Math.pow(coeffArray[i][1] - averageCoeff, 2)
    }
    coeffStdDev = Math.sqrt(coeffDiffSum / coeffArray.length)
    for (let i = 0; i < coeffArray.length / 2; i++) {
	if (coeffArray[i][1] >= averageCoeff + 3 * coeffStdDev) {
	    tauArray.push(coeffArray[i][0])
	}
    }
    for (let i = 0; i < tauArray.length; i++) {
	var diff = tauArray[i] - tauArray[i - 1]
	potentialPeriods[diff] = potentialPeriods[diff]
	    ? potentialPeriods[diff] + 1
	    : 1
    }
    Object.keys(potentialPeriods).forEach(function(potentialPeriod) {
	if (potentialPeriods[potentialPeriod] > periodOccurance) {
	    periodOccurance = potentialPeriods[potentialPeriod]
	    foundPeriod = potentialPeriod
	}
    })
    this.setParam("period", Number(foundPeriod))
    this.redraw()
}

function theta(t, period, offset = 0) {
    return ((2 * Math.PI) / period) * (t + 3 + offset)
}

function startAngle(t, period, offset = 0) {
    return (theta(t - 1, period, offset) + theta(t, period, offset)) / 2
}

function endAngle(t, period, offset = 0) {
    return (theta(t + 1, period, offset) + theta(t, period, offset)) / 2
}

function radius(spacing, angle, radParam = 300) {
    return 150 + radParam + spacing * angle
}

export default Spiral
