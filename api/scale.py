from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
def scale(data):
    return scaler.fit_transform(data)