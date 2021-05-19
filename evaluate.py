import pandas as pd
import numpy as np

df = pd.read_csv("order1_b1.0_scl1.0_seso8.0.csv")
t = df['t']
r = df['r(t)']
y = df['y(t)']
u = df['u(t)']
e = r - y

iae = sum(abs(e)) / len(e)
ise = sum(np.square(e)) / len(e)
print(iae)
print(ise)