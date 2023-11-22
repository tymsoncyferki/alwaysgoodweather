import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

data = pd.read_csv('locations.csv')
y = data['hmax'] # tylko do testów
X = data[['latitude', 'longitude']]
lm = LinearRegression().fit(X.values, y.values)
bialystok = lm.predict(np.array([[53.175887, 19.745537]]))
print(bialystok)