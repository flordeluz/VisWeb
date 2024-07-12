from sklearn.model_selection import cross_val_score
# import pymc3 as pm
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import KNNImputer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import shapiro
from statsmodels.imputation import mice

import concurrent.futures
from functools import partial
import time

# Definir un diccionario compartido para almacenar los resultados
res_threads = []

# dataframe de prueba
sdf = pd.read_csv(
    'C:/Users/ruben/Documents/ProyectoVisWeb/VisWeb/new_api/debug_na.csv')
sdf['date'] = pd.to_datetime(sdf['date'], format="%d/%m/%Y")
sdf = sdf.set_index('date')
print(sdf)
print('____________________________________________________________________________')


def graficoLinea(df):

    # Crear gráfico de líneas
    plt.figure(figsize=(10, 6))

    # Añadir cada variable al gráfico con una etiqueta
    for columna in df.columns:
        plt.plot(df.index, df[columna], label=columna)

    # Configurar título y etiquetas
    plt.title('Gráfico de Líneas de Serie Temporal Multivariada')
    plt.xlabel('Fecha')
    plt.ylabel('Valor')

    # Añadir leyenda
    plt.legend(loc='upper left')

    # Mostrar el gráfico
    plt.show()


def mcar_runstest(df):
    # Función para evaluar si una serie es completamente al azar
    def is_random(series, alpha=0.05):
        z_stat, p_value = sm.stats.runstest_1samp(series > series.median())
        return p_value > alpha
    results = {}
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        else:
            results[feature] = is_random(df[feature])

    # Resultado final (True si alguna de las series son aleatorias, False si no hay ninguna)
    final_result = any(results.values())
    # Mostrar resultados
    print("Resultados por columna:", results)
    print("¿Alguna serie completamente al azar?:", final_result)

    res_threads.append({'message': 'MCAR Run Test', 'status': final_result})
    return final_result


def mcar_runstest2(df):
    result = False
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        else:
            z_stat, p_value = sm.stats.runstest_1samp(
                df[feature] > df[feature].median())
            if p_value > 0.05:
                result = True
            print(
                f"{feature}: p_value = {p_value} - {'Aleatorio' if p_value > 0.05 else 'No Aleatorio'}")

    res_threads.append({'message': 'MCAR Run Test 2', 'status': result})
    return result


def mcar_mdispersion(df):
    result = False
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        else:
            mean = df[feature].mean()
            std_dev = df[feature].std()
            coeff_var = std_dev / mean if mean != 0 else 0  # Coeficiente de variación

            z_stat, p_value = sm.stats.runstest_1samp(
                df[feature] > df[feature].mean())
            is_random = p_value > 0.05
            if p_value > 0.05:
                result = True

            print(f"{feature}: Coef. Var. = {coeff_var} - p_value = {p_value} - {'Aleatorio' if is_random else 'No Aleatorio'}")
    res_threads.append({'message': 'MCAR Medida Dispersion', 'status': result})
    return result


def mcar_mforma(df):
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        else:
            stat, p_value = shapiro(df[feature])
            is_normal = p_value > 0.05  # Nivel de significancia del 5%

            print(
                f"{feature}: p_value = {p_value} - {'Normal' if is_normal else 'No Normal'}")

        # Si todas las variables son normales, podríamos considerar que la serie temporal es aleatoria.
        is_random = any(shapiro(df[col])[1] > 0.05 for col in df.columns)
        print("\nLa serie temporal multivariada es",
              "aleatoria." if is_random else "no aleatoria.")
    res_threads.append(
        {'message': 'MCAR Medida de Forma', 'status': is_random})
    return is_random


def mcar_mcorrelacion(df):
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        # Crear una matriz de correlación
        correlation_matrix = df.corr()

        print("Matriz de Correlación:")
        print(correlation_matrix)

        # Umbral de correlación (ajustable según tu criterio)
        correlation_threshold = 0.5  # puedes ajustar este valor

        # Revisar si hay correlaciones significativas en la matriz de correlación
        is_random = True  # asumir que es aleatorio hasta que se demuestre lo contrario
        for i in range(correlation_matrix.shape[0]):
            # para no repetir pares de correlación
            for j in range(i+1, correlation_matrix.shape[1]):
                if abs(correlation_matrix.iloc[i, j]) > correlation_threshold:
                    is_random = False
                    break

        # Imprimir el resultado
        print("\nLa serie temporal multivariada es",
              "aleatoria." if is_random else "no aleatoria.")

    res_threads.append(
        {'message': 'MCAR Medida de Correlacion', 'status': is_random})
    return is_random


def mcar_mcovarianza(df):
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        # Crear una matriz de covarianza
        covariance_matrix = df.cov()

        print("Matriz de Covarianza:")
        print(covariance_matrix)

        # Umbral de covarianza (ajustable según tu criterio)
        covariance_threshold = 0.1  # puedes ajustar este valor

        # Revisar si hay covarianzas significativas en la matriz de covarianza
        is_random = True  # asumir que es aleatorio hasta que se demuestre lo contrario
        for i in range(covariance_matrix.shape[0]):
            # para no repetir pares de covarianza
            for j in range(i+1, covariance_matrix.shape[1]):
                if abs(covariance_matrix.iloc[i, j]) > covariance_threshold:
                    is_random = False
                    break

        # Imprimir el resultado
        print("\nLa serie temporal multivariada es",
              "aleatoria." if is_random else "no aleatoria.")
    res_threads.append(
        {'message': 'MCAR Medida de Covarianza', 'status': is_random})
    return is_random


# ____________________________________________________________________________


def mcar_glm(df):
    def check_mcar(df, column_name):
        # Crear una columna binaria que sea 1 si el valor es NA y 0 de lo contrario
        df['is_missing'] = df[column_name].isnull().astype(int)

        # Usar todas las demás columnas como predictores
        X = df.drop(columns=['is_missing', column_name])
        X = sm.add_constant(X)
        y = df['is_missing']

        # Ajustar el modelo logístico
        model = sm.GLM(y, X, family=sm.families.Binomial()).fit()

        # Imprimir resumen del modelo
        print(model.summary())

        # Si el p-valor de alguna variable es menor a un cierto umbral (por ejemplo, 0.05)
        # entonces se puede inferir que los datos faltantes no son MCAR.
        significant_vars = model.pvalues[model.pvalues < 0.05]
        return len(significant_vars) == 1 and 'const' in significant_vars

    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        if df[feature].isnull().sum() > 0:
            print(f"Checking MCAR for column {feature}:")
            if check_mcar(df, feature):
                print(f"Data in column {feature} is likely MCAR.\n")
            else:
                print(f"Data in column {feature} is not MCAR.\n")


def mar_glm(df):
    def check_mar(df, column_name):
        # Crear una columna binaria que sea 1 si el valor es NA y 0 de lo contrario
        df['is_missing'] = df[column_name].isnull().astype(int)

        # Usar todas las demás columnas como predictores
        X = df.drop(columns=['is_missing', column_name])
        X = sm.add_constant(X)
        y = df['is_missing']

        # Ajustar el modelo logístico
        model = sm.GLM(y, X, family=sm.families.Binomial()).fit()

        # Imprimir resumen del modelo
        print(model.summary())

        # Si el p-valor de alguna variable (excluyendo la constante) es menor a 0.05,
        # entonces se puede inferir que los datos faltantes son condicionalmente aleatorios (MAR) con respecto a esa variable.
        significant_vars = model.pvalues[(model.pvalues < 0.05) & (
            model.pvalues.index != 'const')]
        return significant_vars

    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        if df[feature].isnull().sum() > 0:
            print(f"Checking MAR for column {feature}:")
            significant_predictors = check_mar(df, feature)
            if not significant_predictors.empty:
                print(
                    f"Data in column {feature} is likely MAR based on these variables: {', '.join(significant_predictors.index)}.\n")
            else:
                print(
                    f"Data in column {feature} is not identified as MAR based on the other variables.\n")


def mar_mice(df):
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
    # Realizando MICE
    imp = mice.MICEData(df)
    imp.update_all(10)  # Realiza 10 ciclos de imputación y actualización

    # Regresión logística para probar si los datos son MAR
    missing_indicator = df[feature].isnull().astype(int)
    model = sm.Logit(missing_indicator, sm.add_constant(df['tempMax'].values))
    result = model.fit()

    print(result.summary())

    # Decision basada en el p-valor
    p_value = result.pvalues[1]
    is_mar = p_value < 0.05

    print(
        f"\nThe data is {'MAR' if is_mar else 'not MAR'} based on a significance level of 0.05.")


def mar_interrupciones(df):
    for feature in df.columns:
        if feature == 'date':
            df[feature] = pd.to_datetime(df[feature])
            df = df.set_index(feature)
        X = y
        n = 100
        # Crear una variable indicadora de datos faltantes
        missing_indicator = np.isnan(df[feature]).astype(int)
        # Generar una variable dependiente y como función de las variables, con algún ruido
        y = 0.5 * feature[:, 0] + 2 * feature[:, 1] + 2 * \
            missing_indicator + np.random.normal(size=n)

        # Ajustar un modelo de regresión incluyendo la variable indicadora de datos faltantes
        X_with_indicator = np.column_stack((X, missing_indicator))
        X_with_indicator = sm.add_constant(X_with_indicator)

        model = sm.OLS(y, X_with_indicator, missing='drop')
        results = model.fit()

        # Imprimir los resultados
        print(results.summary())

        # Evaluar si la variable indicadora de datos faltantes es estadísticamente significativa
        p_value = results.pvalues[-1]
        is_mar = p_value < 0.05

        print(
            f"\nThe missing data is {'MAR' if is_mar else 'not MAR'} based on a significance level of 0.05.")


# TECNICAS DE APRENDIZAJE AUTOMATICO


def mar_desiciontree(sdf):
    # Reemplazar 'tu_columna' con el nombre de la columna que te interesa
    sdf['missing'] = sdf['tempMax'].isnull().astype(int)

    # Separar los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(sdf.drop(columns=['tempMax', 'missing']),
                                                        sdf['missing'],
                                                        test_size=0.2,
                                                        random_state=42)

    # Ajustar un modelo Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Predecir la probabilidad de datos ausentes en el conjunto de prueba
    y_pred = rf_model.predict(X_test)

    # Evaluar el modelo
    print(classification_report(y_test, y_pred))
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy:.4f}')

    # Determinar si los datos están MAR
    # Podemos considerar que si el accuracy es significativamente mejor que adivinar al azar (0.5),
    # entonces es probable que los datos estén MAR.
    is_MAR = accuracy > 0.5

    print(f'Los datos faltantes son MAR: {is_MAR}')


def mcar_mnolineales(sdf):
    from filterpy.monte_carlo import particle_filter
    from statsmodels.tsa.statespace import sarimax
    # Generar datos de ejemplo
    np.random.seed(0)
    n = 100
    y = np.sin(np.linspace(0, 20, n)) + np.random.normal(scale=0.5, size=n)
    y[np.random.randint(0, n, 20)] = np.nan  # Introduce datos faltantes

    # Estimación con el Filtro de Partículas
    endog = pd.Series(y)
    mod = sarimax.SARIMAX(endog, order=(1, 0, 1))
    pf = particle_filter(mod.ssm, filter_method='particle', n_particles=3000)

    # Little's MCAR test (podrías necesitar una función que implemente este test)
    # Este es un pseudocódigo, necesitarías implementar o encontrar una función para realizar el test
    mcar_result = 'littles_mcar_test(y)'  # implement this function

    # Tomar una decisión basada en los resultados
    if mcar_result.p_value > 0.05:
        mar_status = 'TRUE'
    else:
        mar_status = 'FALSE'

    print(f"Evaluación MAR: {mar_status}")


def mar_modelosLogisticos(df):
    result = False
    if df.columns[0] == 'date':
        df.columns[0] = pd.to_datetime(df.columns[0])
        df = df.set_index(df.columns[0])

    def is_mar(data, col_index):
        complete_data = data.copy()
        # print('_______________complete data_____________________', len(complete_data))
        # print(complete_data)

        # eliminamos las filas con datos faltantes en la columna de interés
        # complete_data = complete_data[~np.isnan(complete_data[:, col_index]), :]
        complete_data = complete_data.dropna(subset=[df.columns[col_index]])
        # print(complete_data)
        # print('_______________complete data 2_____________________', len(complete_data))
        # print(complete_data)      #DATOS VACIOS DE LA COLUMNA DE INTERES ELIMINADOS

        # missing_indicator = np.isnan(data[:, col_index])
        missing_indicator = data[data.columns[col_index]].notna().tolist()
        # print('_______________mising indicator_____________________',
        #      len(missing_indicator))  # VER UNA LISTA SI HAY DATOS FALTANTES, TRUE OR FALSE
        # print(missing_indicator)

        X = data.copy()
        # print('_______________X_____________________', len(X))
        # print(X)  # copia de los datos completos, incluidos nan

        # Podemos manejar los valores faltantes de diferentes maneras, una opción es rellenar con ceros.
        X[np.isnan(X)] = 0
        # print('_______________X 2_____________________', len(X))
        # print(X)

        # y = missing_indicator.astype(int)
        y = [int(value) for value in missing_indicator]
        # print('_______________Y_____________________', len(y))
        # print(y)

        model = LogisticRegression(max_iter=200)

        # Se ajusta un modelo logístico y se valida usando validación cruzada
        scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
        # print('_______________Scores_____________________')
        # print(scores)
        # si el AUC es significativamente diferente de 0.5, entonces podríamos decir que hay evidencia de que los datos son MAR
        return np.mean(scores) > 0.6

    for column in range(len(df.columns)):
        if is_mar(df, column):
            # print(f"Column {column} is likely MAR.")
            result = True
        # else:
        #    print(f"Column {column} is likely not MAR.")
    print('Algoritmo MAR: Usando Modelos Logisticos: ', result)
    return result


# graficoLinea(sdf)
# mcar_runstest(sdf)        #listo
# mcar_runstest2(sdf)       #listo
# mcar_mdispersion(sdf)     #listo
# mcar_mforma(sdf)          #listo
# mcar_mcorrelacion(sdf)    #listo
# mcar_mcovarianza(sdf)     #listo

# mcar_glm(sdf)     #NECESITA DATOS COMPLETOS
# mar_glm(sdf)      #NECESITA DATOS COMPLETOS
# mar_mice(sdf)     #NECESITA DATOS COMPLETOS
# mar_interrupciones(sdf)  # NECESITA DATOS COMPLETOS

# mar_desiciontree(sdf)   #DATOS INCOMPLETOS NAN
# mcar_mnolineales(sdf) #DATOS INCOMPLETOS NAN


# PUEDE UTILIZARSE COMO GUIA PARA LOS ALGORITMOS DE MACHINE LEARNING
# mar_modelosLogisticos(sdf)    #listo

# CREACION DE FUNCIONES MULTIHILO
# begin_______________________________________________________________
def ejecutarFuncionesMultihilo(df, arr_func):
    # Crear un objeto ThreadPoolExecutor
    executor = concurrent.futures.ThreadPoolExecutor()

    # Iniciar las tareas y obtener los objetos Future
    futures = [executor.submit(partial(tarea, df)) for tarea in arr_func]
    concurrent.futures.wait(futures)
    executor.shutdown()


# Crear un array con las funciones
array_funciones = [mcar_runstest, mcar_runstest2, mcar_mdispersion,
                   mcar_mforma, mcar_mcorrelacion,
                   mcar_mcovarianza]
# end_______________________________________________________________


def comprobarMcar(dataframe):

    ejecutarFuncionesMultihilo(dataframe, array_funciones)

    val_positivos = 0
    messages = []
    analized = len(res_threads)
    for valor in res_threads:
        if valor['status'] == True:
            val_positivos += 1
            messages.append(valor['message'])
    res_threads.clear()
    print('Algoritmos MCAR ', val_positivos,
          ' de ', analized, ' son positivos.')
    # Si el 50% de los algoritmos son True, retornar
    if val_positivos >= (analized*50/100):
        return True, messages
    else:
        return False, messages


comprobarMcar(sdf)
mar_modelosLogisticos(sdf)
