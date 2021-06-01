from functools import partial
from runkut4_adrc import linear_tracking_differentiator, runkut4
import numpy as np
import matplotlib.pyplot as plt
from functools import partial

T = 0.1
R = 1.
order = 3
A_td = np.zeros((order, order))
B_td = np.array(np.concatenate((np.zeros((order-1, 1)), np.array([[R**order]])), axis=0))
for i in range(order):
	if i < order-1:
		A_td[i][i+1] = 1.
	A_td[order-1][i] = - (2**i) * R ** (order-i)

t = [i*T for i in range(301)]
r = np.square(t)
v_t = np.array([[0], [0], [0]])
new_vt = np.zeros((order, 1))
for i in range(300):
	ltd = partial(linear_tracking_differentiator, A_td, B_td, r[i])
	new_vt = runkut4(ltd, new_vt, T)
	v_t = np.concatenate((v_t, new_vt), axis=1)

plt.subplot(311)
plt.plot(t, v_t[[0]].T)
plt.subplot(312)
plt.plot(t, v_t[[1]].T)
plt.subplot(313)
plt.plot(t, v_t[[2]].T)
plt.show()