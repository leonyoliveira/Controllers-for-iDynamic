from ControlLib import *
from EDO import rungekutta4
import numpy as np
import csv

class LinearADRC(Control): 

	def __init__(self, T, order, s_cl, s_eso, b0):
		super().__init__(T=T, order=order)
		self.s_cl = s_cl
		self.s_eso = s_eso
		self.b0 = b0
		self.A, self.B, self.C, self.sys_pol, self.eso_pol, self.x_t = self.controller_matrices()
		self.u_t = []
		self.t_sim = []
		self.y_t = []
		self.r_t = []
		self.filename = str(order) + str(b0) + str(s_cl) + str(s_eso) + ".csv"
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

		return A, B, C, sys_pol, eso_pol, x_t

	def control(self):
		""" 
		Return the control signal.
		You can access the error at instant 0, -1, and -2 as:
		self.e(0), self.e(-1) and self.e(-2) respectively 

		Obs.: To access more errors, create your controller with the 
		command:
		controller = MyControllerName(T, n)		
		where T is the sampling time (normally 0.3) and n is the order 
		of the controller (how many errors you can access)
		For instance:

		controller = MyControllerName(0.5, 6)

		Will use a controller with 0.5s sampling time and will access
		from self.e(0) up to self.e(-5)
		"""
		A_obs = self.A - np.matmul(np.array([self.eso_pol]).T[1:], self.C)
		self.x_t = rungekutta4(self.T, A_obs, self.B, np.array([self.eso_pol]).T[1:], self.x_t, self.u(), self.y())
		u0 = 0
		for i in range(self.order):
			u0 += (self.r(-i) - self.x_t[i]) * self.sys_pol[self.order-i]

		u = (u0 - self.x_t[self.order]) / self.b0

		self.u_t.append(u[0])
		self.y_t.append(self.y(0))
		self.t_sim.append(self.t())
		self.r_t.append(self.r(0))
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