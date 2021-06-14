from functools import partial
from runkut4_adrc import linear_tracking_differentiator, runkut4
import numpy as np
import matplotlib.pyplot as plt
import math
from functools import partial

T = 0.01
R = 5
order = 2
A_td = np.zeros((order, order))
B_td = np.vstack((np.zeros((order-1, 1)), R**order))
for i in range(order):
	if i < order-1:
		A_td[i][i+1] = 1.
	A_td[order-1][i] = -math.comb(order, i) * R ** (order-i)

t = [i*T for i in range(3001)]
r = [1 for i in range(3001)]
v_t = np.array([[0] for i in range(order)])
new_vt = np.zeros((order, 1))
for i in range(3000):
	ltd = partial(linear_tracking_differentiator, A_td, B_td, r[i])
	new_vt = runkut4(ltd, new_vt, T)
	v_t = np.concatenate((v_t, new_vt), axis=1)

plt.subplot(311)
plt.plot(t, v_t[[0]].T)
plt.subplot(312)
plt.plot(t, v_t[[1]].T)
#plt.subplot(313)
#plt.plot(t, v_t[[2]].T)
plt.show()