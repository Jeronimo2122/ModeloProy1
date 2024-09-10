import pandas as pd
import numpy as np
import sklearn.linear_model as lm
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from scipy import stats

def cargar_datos(datos):
    return pd.read_csv(datos)

def modeloRLS():
    data = cargar_datos('SeoulBikeDataClean.csv')
    X_new = data.drop(['Rented Bike Count','Visibility (10m)'] , axis=1)
    Y_new = data['Rented Bike Count']
    
    X_train, X_test, Y_train, Y_test = train_test_split(X_new, Y_new, test_size=0.2, random_state=0)
    modelo = lm.LinearRegression()
    modelo.fit(X_train, Y_train)

    residuals = Y_test - modelo.predict(X_test)
    sigma = np.std(residuals)

    return  modelo, sigma