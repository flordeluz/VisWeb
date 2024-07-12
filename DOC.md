# Documentación VisWeb

# Operación de Ciclicidad

En el siguiente bloque se obtiene el resultado de la transformada de fourier y también las frecuencias de la transformada. Luego se obtienen las posiciones de los valores más altos (los picos)

```py
y = res_dataframe.values
fourier_output = np.abs(fft.fft(y))
frecuencies = fft.fftfreq(len(y))
peaks = sig.find_peaks(fourier_output, prominence=10**2)[0]
```

Se obtiene la frecuencia de fourier de los picos y también los valores de la transformada en los picos. Luego se crea un Dataframe para almacenar la información de los picos y lo ordenamos según el valor de la transformada de Fourier

```py
print(peaks)
peak_freq = frecuencies[peaks]
peak_power = fourier_output[peaks]

output = pd.DataFrame()

output['index'] = peaks
output['freq (1/hour)'] = peak_freq
output['amplitude'] = peak_power
output['period (days)'] = 1/peak_freq
output['fft'] = fourier_output[peaks]
output = output.sort_values('amplitude', ascending=False)

print(output)
```

Luego se obtienen los valores más altos y calculamos la inversa de la transformada de esos valores.

```py
max_amp_index = output['index'].iloc[0:5:2]

filtered_fft_output = np.array(
    [f if i in max_amp_index.values else 0 for i, f in enumerate(fourier_output)])

filtered_sig = fft.ifft(filtered_fft_output)

```

## SpiralJS

Se hizo uso de una libreria de JS llamada [SpiralJS](https://github.com/WesTyler/SpiralJS) (la cuál crea un objeto SVG con ayuda de la librería D3.js) y se customizó para mostrar la información por mes de acuerdo a la dimensión especificada.

También para personalizar los eventos al pasar el mouse encima de un punto, esto para mostrar los datos con gráficos estrella de ese mes en los años especificados.

Para realizar todo esto la librería de SpiralJS recibe 4 parámetros importantes:

- Un array de números que serán representados en la espiral
- El número de segmentos que habrá en el gráfico (el tamaño del array)
- El número de segmentos por ciclo
- La función que se ejecutará cuando pasemos el mouse por un segmento

```js
var spiral1 = new Spiral("points");
spiral1.option.data = points;
spiral1.setParam("numberOfPoints", segmentsPerCycle * cycles);
spiral1.setParam("period", 12);
spiral1.setParam("hoverFunction", this.showDetails);
spiral1.setParam("svgHeight", window.innerHeight * 0.7);
spiral1.setParam("svgWidth", 650);
spiral1.setParam("spacing", 8);
spiral1.setParam("radiusParam", 150);
```

Una vez ejecutada esta función el espiral está listo para ser renderizado. Para esto se llama a la función `render`, la cual genera genera segmentos en SVG por cada elemento del array respetando los parámetros ingresados (radiusParam y spacing). Dado que la espiral usa colores para indicar que tan alto o bajo es el valor de la data se ha introdujo una leyenda para mapear los valors numéricos.

**Generacion de espiral**
```js
svg
    .selectAll('g')
    .selectAll('path')
    .data(option.data)
    .enter()
    .append('path')
    .style('opacity', '0')
    .attr('fill', function(d) {
      return colorScale(d[2])
    })
    .attr('d', function(d) {
      return d[1]
    })
    .on('mouseover', function(values, idx) {
      let comp_idx = idx % segmentsPerCycle
      let circles = this.parentElement.children
      while (comp_idx < option.data.length) {
        circles[comp_idx].setAttribute('stroke', 'black')
        circles[comp_idx].setAttribute('stroke-width', '1')
        comp_idx += segmentsPerCycle
      }
      option.hoverFunction(values, idx)
    })
    .on('mouseout', function(v, idx) {
      let comp_idx = idx % segmentsPerCycle
      let circles = this.parentElement.children
      while (comp_idx < option.data.length) {
        circles[comp_idx].setAttribute('stroke', 'none')
        comp_idx += segmentsPerCycle
      }
    })
```

**Generacion de leyenda**


```js
let min = d3.min(option.data, d => d[2])
  let max = d3.max(option.data, d => d[2])

  let colorScale = d3
    .scaleLinear()
    .domain([min, max])
    .range(['#fff33b', '#e93e3a'])
```


El hecho de que podamos cambiar el número de segmentos, así como también el número de ciclos o el radio es lo que nos abre la posibilidad de interacción del usuario con la herramienta dinámicamente. Por lo cual es totalmente factible hacer que estos parámetros cambien y afecten a los gráficos según la necesidad del usuario.
