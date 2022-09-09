const d3 = require('d3')

function Spiral(graphType) {
  this.option = {
    graphType: graphType || 'points',
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
    targetElement: '#chart',
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
    color: 'black',
    colorMode: 'opacity'
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
    var rad = radius(option.spacing, angle) + 150
    var size = option.data[index][1]

    temp_data.push(this.cartesian(rad, angle, size))
  }
  option.data = temp_data
}

Spiral.prototype.render = function() {
  console.log('Rendering Spiral')
  var classObj = this
  var option = classObj.option

  var svg = d3
    .select(option.targetElement)
    .append('svg')
    .attr('width', option.svgWidth)
    .attr('height', option.svgHeight)

  if (option.graphType === 'points') {
    svg
      .append('g')
      .attr(
        'transform',
        'translate(' + option.margin.left + ',' + option.margin.top + ')'
      )

    svg
      .selectAll('g')
      .selectAll('dot')
      .data(option.data)
      .enter()
      .append('circle')
      .style('opacity', '0')
      .style('fill', 'cornflowerblue')
      .attr('r', function(d) {
        return d[2]
      })
      .attr('cx', function(d) {
        return d[0]
      })
      .attr('cy', function(d) {
        return d[1]
      })
      .on('mouseover', option.hoverFunction)
      .append('svg:title')
      .text((d, i) => {
        // console.log('owo:', i, d)
        return `${option.dates[i].date}`
      })
    // animate SVG
    svg
      .selectAll('circle')
      .transition()
      .delay(function(d, i) {
        return i * 50
      })
      .duration(300)
      .style('opacity', '1')

    // Labels
    var id = d3.selectAll('.love-spiral')._groups.length

    var segmentLabels = [
      'December',
      'November',
      'October',
      'September',
      'August',
      'July',
      'June',
      'May',
      'April',
      'March',
      'February',
      'January'
    ]
    // var segmentLabelOffset = 14
    var r = 55
    var labels = svg
      .append('g')
      .classed('labels', true)
      .classed('segment', true)
      .attr(
        'transform',
        `translate(${option.svgWidth / 2 + 10},${option.svgHeight / 2 +
          5}) rotate(-10)`
      )

    labels
      .append('def')
      .append('path')
      .attr('id', 'segment-label-path-' + id)
      .attr('d', 'm0 -' + r + ' a' + r + ' ' + r + ' 0 1 1 -1 0')

    labels
      .selectAll('text')
      .data(segmentLabels)
      .enter()
      .append('text')
      .append('textPath')
      .attr('xlink:href', '#segment-label-path-' + id)
      .attr('startOffset', function(d, i) {
        return (i * 100) / 12 + '%'
      })
      .text(function(d) {
        let month = segmentLabels.indexOf(d) + 1

        return ('0' + month).slice(-2)
      })
  }
}

Spiral.prototype.randomData = function() {
  var classObj = this
  var option = classObj.option

  option.data = []
  for (var i = 0; i < option.numberOfPoints; i++) {
    var angle = theta(i, option.period)
    var rad = radius(option.spacing, angle)
    var size = 1 + Math.random() * 1.5
    if (i % 10 === 0) {
      size = 1.5 + Math.random() * 3
    }

    if (option.graphType === 'non-spiral') {
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
      'svgHeight',
      'svgWidth',
      'margin.top',
      'margin.right',
      'margin.bottom',
      'margin.left'
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
  while (graphContainer.firstChild) {
    graphContainer.removeChild(graphContainer.firstChild)
  }
  classObj.render()
}

Spiral.prototype.autocorrelate = function() {
  var n = this.option.numberOfPoints
  var index = this.option.graphType === 'non-spiral' ? 1 : 2

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

  this.setParam('period', Number(foundPeriod))
  this.redraw()
}

function theta(t, period, offset = 0) {
  return ((2 * Math.PI) / period) * (t + 3 + offset)
}

// function startAngle(t, period) {
//   return (theta(t - 1, period) + theta(t, period)) / 2
// }

// function endAngle(t, period) {
//   return (theta(t + 1, period) + theta(t, period)) / 2
// }

// function colorSelector(datum, opacityFlag) {
//   if (opacityFlag) {
//     return datum[2] / 9
//   } else {
//     //d3 color scale
//   }
// }

function radius(spacing, angle) {
  return spacing * angle
}

export default Spiral
