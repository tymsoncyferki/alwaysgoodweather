import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from plotnine import geom_point, ggplot, aes

data = pd.read_csv('../data/locations.csv')
y = data['hmax']  # only for tests
X = data[['latitude', 'longitude']]
lm = LinearRegression().fit(X.values, y.values)
bialystok = lm.predict(np.array([[53.175887, 19.745537]]))


print(bialystok)
