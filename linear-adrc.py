from ControlLib import *
from runkut4_adrc import *
from functools import partial
import numpy as np
import math
import os
import csv

class LinearADRC(Control): 

	def __init__(self, T, order, s_cl, s_eso, b0, R):
		super().__init__(T=T, order=order)
		self.s_cl = s_cl
		self.s_eso = s_eso
		self.b0 = b0
		self.R = R
		self.A, self.B, self.C, self.A_td, self.B_td, self.K, self.L, self.v_t, self.x_t = self.ADRC_matrices()
		self.filename = "sim_results_adrc/l_" + str(order) + "_" + str(b0) + "_" + str(s_cl) + "_" + str(s_eso) + "_" + ".csv"
		if not os.path.isdir("sim_results_adrc"):
			os.mkdir("sim_results_adrc")
		with open(self.filename, 'w') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writeheader()

	def ADRC_matrices(self):
		v_t = np.zeros((order, 1))
		x_t = np.zeros((order+1, 1))
		A = np.zeros((order+1, order+1))
		B = np.vstack((np.zeros((order-1, 1)), b0, 0))
		C = np.hstack((1, np.zeros(order)))
		K = np.zeros(order)
		L = np.zeros((order+1, 1))
		A_td = np.zeros((order, order))
		B_td = np.vstack((np.zeros((order-1, 1)), self.R**order))
		for i in range(order):
			if i < order-1:
				A_td[i][i+1] = 1.
			A_td[order-1][i] = -math.comb(order, i) * self.R ** (order-i)
			A[i][i+1] = 1.
			K[i] = math.comb(order, order-i) * math.pow(s_cl, order-i)
			L[i][0] = math.comb(order+1, i+1) * math.pow(s_eso, i+1)
		L[order][0] = math.comb(order+1, order+1) * math.pow(s_eso, order+1)
		return A, B, C, A_td, B_td, K, L, v_t, x_t

	def control(self):
		ltd = partial(linear_tracking_differentiator, self.A_td, self.B_td, self.r())
		self.v_t = runkut4(ltd, self.v_t, self.T)
		leso = partial(linear_extended_state_observer, self.A, self.B, self.L, self.u(), self.y())
		self.x_t = runkut4(leso, self.x_t, self.T)

		u0 = 0
		for i in range(self.order):
			u0 += (self.v_t[i] - self.x_t[i]) * self.K[i]
		u = (u0 - self.x_t[self.order]) / self.b0
		
		with open(self.filename, 'a+') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writerow({'t': self.t(), 'r(t)' : self.r(0), 'y(t)' : self.y(0), 'u(t)' : u[0]})
		return u[0]

print("Define system's order:")
order = int(input())
print("Define b0 parameter:")
b0 = float(input())
print("Define system's closed loop poles location:")
s_cl = float(input())
print("Define ESO poles location:")
s_eso = float(input())
print("Define TD maximum acceleration:")
R = float(input())

controller = LinearADRC(T=0.1, order=order, s_cl=s_cl, s_eso=s_eso, b0=b0, R=R)
rc = RemoteControl(controller)
rc.run()