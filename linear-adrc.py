from ControlLib import *
from runkut4_adrc import *
from functools import partial
import numpy as np
import os
import csv

class LinearADRC(Control): 

	def __init__(self, T, order, s_cl, s_eso, b0):
		super().__init__(T=T, order=order)
		self.s_cl = s_cl
		self.s_eso = s_eso
		self.b0 = b0
		self.A, self.B, self.C, self.K, self.L, self.x_t = self.controller_matrices()
		self.A_obs = self.A - np.matmul(self.L , self.C)
		self.filename = "sim_results_adrc/l_" + str(order) + "_" + str(b0) + "_" + str(s_cl) + "_" + str(s_eso) + "_" + ".csv"
		if not os.path.isdir("sim_results_adrc"):
			os.mkdir("sim_results_adrc")
		with open(self.filename, 'w') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writeheader()

	def controller_matrices(self):
		sys_base_pol = np.array([1., self.s_cl]) 
		eso_base_pol = np.array([1., self.s_eso]) 
		x_t = np.zeros((self.order+1, 1))
		A = np.zeros((self.order+1, self.order+1))
		B = np.zeros((self.order+1, 1))
		C = np.array([np.concatenate((1, np.zeros(self.order)), axis=None)])
		sys_pol = np.array([1.]) 
		eso_pol = np.array([1., self.s_eso]) 
		for i in range(self.order):
			A[i][i+1] = 1.
			sys_pol = np.polymul(sys_pol, sys_base_pol)
			eso_pol = np.polymul(eso_pol, eso_base_pol)
		B[self.order-1][0] = self.b0
		K = np.flip(sys_pol)[:self.order]
		L = np.array([eso_pol]).T[1:]
		return A, B, C, K, L, x_t

	def control(self):
		leso = partial(linear_extended_state_observer, self.A_obs, self.B, self.L, self.u(), self.y())
		self.x_t = runkut4(leso, self.x_t, self.T)
		u0 = 0
		for i in range(self.order):
			if i == 0:
				u0 += (self.r(i) - self.x_t[i]) * self.K[i]
			else:
				u0 -= self.x_t[i] * self.K[i]

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

controller = LinearADRC(T=0.1, order=order, s_cl=s_cl, s_eso=s_eso, b0=b0)
rc = RemoteControl(controller)
rc.run()