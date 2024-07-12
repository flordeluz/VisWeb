# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

import pandas as pd
import numpy as np
from scipy.fftpack import fft
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.seasonal import STL
from scipy.stats import pearsonr
from scipy.optimize import curve_fit
from sklearn.preprocessing import MaxAbsScaler

#Librería para la ejecución paralela
import concurrent.futures
from functools import partial
import time

# Definir un diccionario compartido para almacenar los resultados
res_threads = []

            
def detecta_ciclo(serie_temporal, frecuencia_muestral):
    # Realiza la transformada de Fourier de los datos
    transformada_fourier = np.abs(fft(serie_temporal))
    # Encuentra la frecuencia con la potencia máxima (ignorando la frecuencia cero)
    frecuencias = np.fft.fftfreq(len(serie_temporal), 1/frecuencia_muestral)
    frecuencia_ciclo = frecuencias[1:][np.argmax(transformada_fourier[1:])]
    # Calcula la duración del ciclo
    duracion_ciclo = 1 / frecuencia_ciclo
    print("[ FFT Cycle, freq:", frecuencia_ciclo, "time span:", duracion_ciclo, "]")
    # Devuelve True si la duración del ciclo es mayor o igual a 1
    return duracion_ciclo >= 1.0, duracion_ciclo


def verificar_ciclo_fft(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    duracion_ciclo_umbral = 1.0  # Define el umbral de duración del ciclo
    frecuencia_muestral = 1.0  # Define la frecuencia de muestreo
    ciclo = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclo_detectado, ventana_ciclo = detecta_ciclo(serie_temporal, frecuencia_muestral)
        if ciclo_detectado: 
            ciclo = True
            break
        #
    print("[ FFT Cycle Detected:", ciclo, "]")
    res_threads.append({"message": "FFT Cycle Detected", "status": ciclo})
    return ciclo, ventana_ciclo
            

def consistencia_ciclo_fft(serie_temporal, ventana, umbral_varianza):
    n = len(serie_temporal)
    potencias_ciclo = []
    for i in range(n - ventana + 1):
        # Toma un segmento de la serie temporal
        segmento = serie_temporal[i:i+ventana]
        transformada_fourier = np.abs(fft(segmento))
        # Encuentra la potencia del ciclo principal
        potencia_ciclo = np.max(transformada_fourier[1:])
        potencias_ciclo.append(potencia_ciclo)
        #
    varianza = np.var(potencias_ciclo)
    # Devuelve True si la varianza es menor que el umbral
    return varianza < umbral_varianza


def verificar_consistencia_fft(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    ventana = 365*2  # Define el tamaño de la ventana
    umbral_varianza = 1.0  # Define el umbral de varianza
    consistencia = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclos_consistentes = consistencia_ciclo_fft(serie_temporal, ventana, umbral_varianza)
        if ciclos_consistentes:
            consistencia = True
            break
        #
    print("[ FFT Consistency Test:", consistencia, "]")
    res_threads.append({"message": "FFT Consistency Test", "status": consistencia})
    return consistencia


def consistencia_ciclo_acf(serie_temporal, ventana, umbral_varianza):
    n = len(serie_temporal)
    picos_acf = []
    for i in range(n - ventana + 1):
        # Toma un segmento de la serie temporal
        segmento = serie_temporal[i:i+ventana]
        autocorrelacion = acf(segmento, fft=True, nlags=ventana)
        # Encuentra el pico de la ACF (excluyendo el retardo cero)
        pico_acf = np.argmax(autocorrelacion[1:]) + 1
        picos_acf.append(pico_acf)
        #
    varianza = np.var(picos_acf)
    # Devuelve True si la varianza es menor que el umbral
    return varianza < umbral_varianza


def verificar_consistencia_acf(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    ventana = 365*2  # Define el tamaño de la ventana
    umbral_varianza = 1.0  # Define el umbral de varianza
    consistencia = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclos_consistentes = consistencia_ciclo_acf(serie_temporal, ventana, umbral_varianza)
        if ciclos_consistentes:
            consistencia = True
            break
        #
    print("[ ACF Consistency Test:", consistencia, "]")
    res_threads.append({"message": "ACF Consistency Test", "status": consistencia})
    return consistencia


def verificar_consistencia_forma_duracion(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    n_cycles = 3
    consistencia = False
    for feature in dataframe.columns:
        cycle_length = int(len(dataframe[feature]) / n_cycles)
        # Calculamos la desviación estándar de cada ciclo
        cycle_stds = np.zeros(n_cycles)
        for i in range(n_cycles):
            start_index = i * cycle_length
            end_index = start_index + cycle_length
            cycle_data = dataframe[feature][start_index:end_index]
            cycle_stds[i] = np.std(cycle_data)
            #
        mean_cycle_std = np.mean(cycle_stds)
        std_cycle_std = np.std(cycle_stds)
        mean_std_cycle_std = np.mean(std_cycle_std)
        # Comprobamos si la variabilidad es constante
        if np.isclose(std_cycle_std, 0) and np.isclose(mean_std_cycle_std, 0):
            consistencia = True
            break
        #
    print("[ Shape and Time Span Consistency Test:", consistencia, "]")
    res_threads.append({"message": "Shape and Time Span Consistency Test", "status": consistencia})
    return consistencia


def consistencia_ciclo_varianza(serie_temporal, duracion_ciclo, umbral_varianza):
    segmentos = serie_temporal.reshape(-1, duracion_ciclo)
    # Calcula la varianza de cada punto del ciclo a lo largo de los segmentos
    varianzas = np.var(segmentos, axis=0)
    # Calcula la varianza media
    varianza_media = np.mean(varianzas)
    # Devuelve True si la varianza media es menor que el umbral
    return varianza_media < umbral_varianza


def verificar_consistencia_varianza(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    duracion_ciclo = 365*2  # Define la duración del ciclo
    umbral_varianza = 1.0  # Define el umbral de varianza
    consistencia = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        # Asegúrate de que la longitud de la serie temporal sea un múltiplo de "duracion_ciclo"
        serie_temporal = serie_temporal[:len(serie_temporal) // duracion_ciclo * duracion_ciclo]
        ciclos_consistentes = consistencia_ciclo_varianza(serie_temporal, duracion_ciclo, umbral_varianza)
        if ciclos_consistentes:
            consistencia = True
            break
        #
    print("[ Variance Consistency Test:", consistencia, "]")
    res_threads.append({"message": "Variance Consistency Test", "status": consistencia})
    return consistencia


def consistencia_ciclo_pearsonr(serie_temporal, factor_externo, ventana, umbral_correlacion):
    n = len(serie_temporal)
    correlaciones = []
    for i in range(n - ventana + 1):
        # Toma un segmento de la serie temporal y del factor externo
        segmento = serie_temporal[i:i+ventana]
        factor_externo_segmento = factor_externo[i:i+ventana]
        # Calcula la correlación entre el segmento y el factor externo
        correlacion, _ = pearsonr(segmento, factor_externo_segmento)
        correlaciones.append(correlacion)
        #
    correlacion_media = np.mean(correlaciones)
    # Devuelve True si la correlación media es mayor que el umbral
    return correlacion_media > umbral_correlacion


def verificar_consistencia_pearsonr(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    ventana = 365*2  # Define el tamaño de la ventana
    umbral_correlacion = 0.5  # Define el umbral de correlación
    consistencia = False
    factor_externo = np.random.normal(0, 1, len(dataframe))  # Aquí usarías tus datos de factores externos
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclos_consistentes = consistencia_ciclo_pearsonr(serie_temporal, factor_externo, ventana, umbral_correlacion)
        if ciclos_consistentes:
            consistencia = True
            break
        #
    print("[ Pearsonr Consistency Test:", consistencia, "]")
    res_threads.append({"message": "Pearsonr Consistency Test", "status": consistencia})
    return consistencia


def sinusoidal(x, a, b, c, d):
    return a * np.sin(b * x + c) + d


def forma_ciclos_sinusoidal(serie_temporal, periodo, umbral_error):
    stl = STL(serie_temporal, period=periodo)
    result = stl.fit()
    # Ajusta una función sinusoidal al componente estacional
    x = np.arange(len(result.seasonal))
    params, _ = curve_fit(sinusoidal, x, result.seasonal)
    # Calcula el error cuadrático medio
    error = np.mean((result.seasonal - sinusoidal(x, *params))**2)
    # Devuelve True si el error es menor que el umbral
    return error < umbral_error


def verificar_ciclos_sinusoidal(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    periodo = 365*2  # Define el periodo de los ciclos
    umbral_error = 1.0  # Define el umbral de error
    ciclo = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclos_sinusoidales = forma_ciclos_sinusoidal(serie_temporal, periodo, umbral_error)
        if ciclos_sinusoidales:
            ciclo = True
            break
        #
    print("[ Sinusoidal Cycle Test:", ciclo, "]")
    res_threads.append({"message": "Sinusoidal Cycle Test", "status": ciclo})
    return ciclo


def frecuencia_ciclos_fft(serie_temporal, frecuencia_minima, frecuencia_maxima):
    fft = np.fft.fft(serie_temporal)
    fft = fft[:len(fft)//2]
    # Calcula las frecuencias absolutas correspondientes a cada valor FFT
    frecuencias_absolutas = np.abs(np.fft.fftfreq(len(serie_temporal), 1)[:len(fft)])
    # Encuentra la frecuencia con la amplitud más alta
    frecuencia_principal = frecuencias_absolutas[np.argmax(np.abs(fft))]
    # Devuelve True si la frecuencia principal está dentro del rango especificado
    return frecuencia_minima <= frecuencia_principal <= frecuencia_maxima


def verificar_frecuencia_fft(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    frecuencia_minima = 0.02  # Define la frecuencia mínima
    frecuencia_maxima = 0.03  # Define la frecuencia máxima
    frecuencia = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclos_frecuencia_correcta = frecuencia_ciclos_fft(serie_temporal, frecuencia_minima, frecuencia_maxima)
        if ciclos_frecuencia_correcta:
            frecuencia = True
            break
        #
    print("[ FFT Frecuency Test:", frecuencia, "]")
    res_threads.append({"message": "FFT Frecuency Test", "status": frecuencia})
    return frecuencia


def frecuencia_ciclos_acf(serie_temporal, retraso_minimo, retraso_maximo):
    autocorrelacion = acf(serie_temporal, fft=True, nlags=len(serie_temporal)//2)
    # Encuentra los picos de la autocorrelación (ignorando el retardo cero)
    picos = (np.diff(np.sign(np.diff(autocorrelacion))) < 0)
    picos = np.concatenate(([False], picos, [False]))
    # Encuentra los retrasos correspondientes a los picos
    retrasos = np.where(picos)[0]
    # Devuelve True si todos los retrasos están dentro del rango especificado
    return np.all((retraso_minimo <= retrasos) & (retrasos <= retraso_maximo))


def verificar_frecuencia_acf(X):
    if "date" in X.columns:
        X["date"] = pd.to_datetime(X["date"])
        X = X.set_index("date")
        #
    sc = MaxAbsScaler()
    dataframe = pd.DataFrame(sc.fit_transform(X), index = X.index, columns = X.columns)
    retraso_minimo = 350  # Define el retraso mínimo (en días, si tus datos son diarios)
    retraso_maximo = 380  # Define el retraso máximo (en días, si tus datos son diarios)
    frecuencia = False
    for feature in dataframe.columns:
        serie_temporal = dataframe[feature].values
        ciclos_frecuencia_correcta = frecuencia_ciclos_acf(serie_temporal, retraso_minimo, retraso_maximo)
        if ciclos_frecuencia_correcta:
            frecuencia = True
            break
        #
    print("[ ACF Frecuency Test:", frecuencia, "]")
    res_threads.append({"message": "ACF Frecuency Test", "status": frecuencia})
    return frecuencia


# Crear un array con las funciones
array_funciones = [ verificar_ciclo_fft, verificar_consistencia_fft,
                    verificar_consistencia_acf, verificar_consistencia_forma_duracion,
                    verificar_consistencia_varianza, verificar_consistencia_pearsonr,
                    verificar_ciclos_sinusoidal, verificar_frecuencia_fft,
                    verificar_frecuencia_acf
                   ]


# CREACION DE FUNCIONES MULTIHILO
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()
    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()

    
def comprobarCiclicidad(dataframe, par = True):
    if par:
        ejecutarFuncionesMultihilo(dataframe, array_funciones)
        #
    else:
        verificar_ciclo_fft(dataframe)
        verificar_consistencia_fft(dataframe)
        verificar_consistencia_acf(dataframe)
        verificar_consistencia_forma_duracion(dataframe)
        verificar_consistencia_varianza(dataframe)
        verificar_consistencia_pearsonr(dataframe)
        verificar_ciclos_sinusoidal(dataframe)
        verificar_frecuencia_fft(dataframe)
        verificar_frecuencia_acf(dataframe)
        #
    val_positivos = 0
    messages = []
    analized = len(res_threads)
    for valor in res_threads:
        if valor["status"] == True: 
            val_positivos+=1
            messages.append(valor["message"])
            #
    res_threads.clear()
    print("[ Algoritmos Ciclicidad ",val_positivos, " de ", analized, " son positivos. ]")
    #Si el 50% de los algoritmos son True, retornar
    if val_positivos >= (analized*50/100): return True, messages
    else: return False, messages


# def tiemposDeEjecucion(df, arr_func):
#     for funcion in arr_func:
#         inicio = time.time()
#         funcion(df)
#         fin = time.time()
#         tiempo_ejecucion = fin - inicio
#         print(funcion)
#         print(f"Tiempo de ejecución: {tiempo_ejecucion} segundos")
#         print("")
#         res_threads.clear()

# tiemposDeEjecucion(station_df, array_funciones)
