//defines the spiral

// import { d3 } from 'd3'
const d3 = require('d3')
console.log(d3)
var color = d3.scaleOrdinal().range(['#b1475e', '#f5cba0'])

function Spiral(graphType) {
  this.option = {
    graphType: graphType || 'points',
    numberOfPoints: null,
    period: null,
    margin: {
      top: 30,
      right: 10,
      bottom: 30,
      left: 10
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
//methods on the spiral
Spiral.prototype.cartesian = function(radius, angle, size) {
  var classObj = this
  var option = classObj.option

  size = size || 1
  var xPos = option.x(radius * Math.cos(angle))
  var yPos = option.y(radius * Math.sin(angle))
  return [xPos, yPos, size]
}

Spiral.prototype.render = function() {
  var classObj = this
  var option = classObj.option
  var end
  var svg = d3
    .select(option.targetElement)
    .append('svg')
    .attr('width', option.svgWidth)
    .attr('height', option.svgHeight)

  option.data.forEach(function(datum, t) {
    var start = startAngle(t, option.period, option.offset)
    end = endAngle(t, option.period, option.offset)

    var startCenter = radius(option.spacing, start)
    var endCenter = radius(option.spacing, end)
    var startInnerRadius = startCenter - option.lineWidth * 0.5
    var startOuterRadius = startCenter + option.lineWidth * 0.5
    var endInnerRadius = endCenter - option.lineWidth * 0.5
    var endOuterRadius = endCenter + option.lineWidth * 0.5

    var ctrlInnerRad = 0.01
    var ctrlOuterRad = 0.01
    var angle = theta(t, option.period, option.offset)
    var rad = radius(option.spacing, angle)
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
    var arcPath =
      'M' +
      startPoint[0] +
      ' ' +
      startPoint[1] +
      'L' +
      point2[0] +
      ' ' +
      point2[1]
    arcPath +=
      'Q' +
      outerControlPoint[0] +
      ' ' +
      outerControlPoint[1] +
      ' ' +
      point3[0] +
      ' ' +
      point3[1]
    arcPath += 'L' + point4[0] + ' ' + point4[1]
    arcPath +=
      'Q' +
      innerControlPoint[0] +
      ' ' +
      innerControlPoint[1] +
      ' ' +
      startPoint[0] +
      ' ' +
      startPoint[1] +
      'Z'
    datum[1] = arcPath
  })
  //translate the group
  svg
    .append('g')
    .classed('love-spiral', true)
    .attr(
      'transform',
      'translate(' + option.margin.left + ',' + option.margin.top + ')'
    )

  //create the spiral svg
  svg
    .selectAll('g')
    .selectAll('path')
    .data(option.data)
    .enter()
    .append('path')
    .style('fill', function(d) {
      return colorSelector(d)
    })
    .style('opacity', '0')
    .attr('d', function(d) {
      return d[1]
    })
    .on('mouseover', function(d) {
      moveLovebirds(d[0], d[2], d[3])
    })
    .append('svg:title')
    .text(function(d) {
      return d[0]
    })
  //show the spiral in an animation
  svg
    .selectAll('path')
    .transition()
    .delay(function(d, i) {
      return i * 5
    })
    .duration(400)
    .style('opacity', '1')

  // Unique id so that the text path defs are unique - is there a better way to do this?
  var id = d3.selectAll('.love-spiral')._groups.length
  //Radial label
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
  //   var segmentLabelOffset = 14
  var r = 125
  var labels = svg
    .append('g')
    .classed('labels', true)
    .classed('segment', true)
    .attr('transform', 'translate(330,345)')

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
      return d
    })
} //end of render

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

function startAngle(t, period, offset = 0) {
  return (theta(t - 1, period, offset) + theta(t, period, offset)) / 2
}

function endAngle(t, period, offset = 0) {
  return (theta(t + 1, offset) + theta(t, offset)) / 2
}

function radius(spacing, angle) {
  return 300 + spacing * angle
}

function colorSelector(datum) {
  if (datum[2] == datum[3]) {
    return color(0)
  } else {
    return color(1)
  }
}

//move both circles
function moveLovebirds(day) {
  d3.select('.day span').text(day)

  d3.selectAll('.city-label').classed('notVisible', true)

  //   for (let i = 0; i < citiesData.length; i++) {
  //     if (citiesData[i].city == cityDiana) {
  //       movePerson(
  //         'diana',
  //         citiesData[i].lon,
  //         citiesData[i].lat,
  //         5,
  //         citiesData[i].city
  //       )
  //     } //end if
  //     if (citiesData[i].city == cityManolo) {
  //       movePerson(
  //         'manolo',
  //         citiesData[i].lon,
  //         citiesData[i].lat,
  //         -5,
  //         citiesData[i].city
  //       )
  //     } //end if
  //   } //end for
}
//move one person
// function movePerson(person, lon, lat, space, city) {
//   d3.selectAll('.' + person)
//     .transition()
//     .duration(100)
//     .attr('cx', projection([lon, lat])[0] + space)
//     .attr('cy', projection([lon, lat])[1])

//   d3.selectAll('.' + city).classed('notVisible', false)
// }

export default Spiral
