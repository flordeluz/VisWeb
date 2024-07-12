from sklearn.decomposition import PCA
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd
import numpy as np

knn_imputer = KNNImputer(missing_values=-1, n_neighbors=10, weights="uniform")
simple_imp = SimpleImputer(missing_values=-1, strategy='mean')
iter_imp = IterativeImputer(missing_values=-1, max_iter=20)

minmax_scaler = MinMaxScaler()
sc_scaler = StandardScaler()

# dataframe de prueba
station_df = pd.read_csv('C:/Users/ruben/Documents/ProyectoVisWeb/VisWeb/new_api/debug.csv')
station_df['date'] = pd.to_datetime(station_df['date'])
station_df = station_df.set_index('date')

global current_df
current_df = station_df

def reduce_pca(n_comp):
    n_comp = int(n_comp)
    pca = PCA(n_comp)
    # dates, data = read_dataset(dataset)
    global current_df
    data = current_df.values
    print(data)
    data[data < 0] = -1
    data = sc_scaler.fit_transform(data)
    data = pca.fit_transform(data)
    df = pd.DataFrame(data, columns=range(1, n_comp+1), index=current_df.index)
    current_df = df
    print(current_df)
    return current_df

def reduce_correlation():
    global current_df
    df = current_df
    threshold=0.8
    print(df)
    corr_matrix = df.corr().abs()
    # Selecciona la parte superior del triángulo de la matriz de correlación
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool_))
    # Encuentra índices de columnas de características con correlación mayor que el umbral
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    if len(to_drop) > 0:
        print(to_drop)
    # Reduce las variables
    reduced_df = df.drop(df[to_drop], axis=1)
    print(reduced_df)
    return reduced_df

def reduce_rfc(threshold = "median"):
     # Ejemplo de uso
    # X es una matriz de características de la serie temporal multivariada
    X = np.random.rand(100, 10)  # Ejemplo aleatorio de 100 instancias y 10 características
    y = np.random.randint(0, 2, 100)  # Etiquetas binarias aleatorias

    # Construir el modelo de clasificación
    #clf = RandomForestClassifier()
    #clf.fit(X, y)

    # Seleccionar características basadas en importancia
    #feature_selector = SelectFromModel(clf, threshold=threshold, prefit=True)
    #selected_features = feature_selector.get_support(indices=True)

    # Determinar si la reducción de dimensionalidad es apropiada
    #result = len(selected_features) < X.shape[1]

    # Devolver True si la reducción de dimensionalidad es apropiada, False en caso contrario
    #return result

#reduce_pca(2)
reduce_correlation()