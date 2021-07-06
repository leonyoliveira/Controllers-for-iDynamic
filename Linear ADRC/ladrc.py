import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
system = "temp_test"
datadir = os.path.join(currentdir, ("data_" + system))

import random
from ControlLib import *
from runkut4_adrc import *
from functools import partial
import numpy as np
import math
import csv

class LADRC(Control): 

	def __init__(self, T, order, s_cl, s_eso, b0, R):
		super().__init__(T=T, order=order)
		self.update_LADRC(order, s_cl, s_eso, b0, R)
		self.v_t = np.zeros((self.order, 1))
		self.x_t = np.zeros((self.order+1, 1))
		self.sp = -1
		self.stop_flag = 0
		self.filename = datadir + "/" + str(order) + "_" + str(b0) + "_" + str(s_cl) + "_" + str(s_eso) + "_" + str(R) + "_" + ".csv"
		if not os.path.isdir(datadir):
			os.mkdir(datadir)
		with open(self.filename, 'w') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writeheader()

	def update_LADRC(self, order, s_cl, s_eso, b0, R):
		self.s_cl = s_cl
		self.s_eso = s_eso
		self.b0 = b0
		self.R = R
		self.A, self.B, self.C, self.A_td, self.B_td, self.K, self.L = self.ADRC_matrices()

	def update_setpoint(self, sp):
		self.sp = sp

	def ADRC_matrices(self):
		A = np.zeros((self.order+1, self.order+1))
		B = np.vstack((np.zeros((self.order-1, 1)), self.b0, 0))
		C = np.hstack((1, np.zeros(self.order)))
		K = np.zeros(self.order)
		L = np.zeros((self.order+1, 1))
		A_td = np.zeros((self.order, self.order))
		B_td = np.vstack((np.zeros((self.order-1, 1)), self.R**self.order))
		for i in range(self.order):
			if i < self.order-1:
				A_td[i][i+1] = 1.
			A_td[self.order-1][i] = -math.comb(self.order, i) * self.R ** (self.order-i)
			A[i][i+1] = 1.
			K[i] = math.comb(self.order, self.order-i) * math.pow(self.s_cl, self.order-i)
			L[i][0] = math.comb(self.order+1, i+1) * math.pow(self.s_eso, i+1)
		L[self.order][0] = math.comb(self.order+1, self.order+1) * math.pow(self.s_eso, self.order+1)
		return A, B, C, A_td, B_td, K, L

	def set_point(self):
		return self.sp

	def stop(self):
		return self.stop_flag

	def stop_press(self):
		self.stop_flag = 1

	def control(self):
		yn = self.y() + random.uniform(-0.05,0.05) * self.r()
		ltd = partial(linear_tracking_differentiator, self.A_td, self.B_td, self.r())
		self.v_t = runkut4(ltd, self.v_t, self.T)
		leso = partial(linear_extended_state_observer, self.A, self.B, self.L, self.u(), yn)
		self.x_t = runkut4(leso, self.x_t, self.T)

		u0 = 0
		for i in range(self.order):
			u0 += (self.v_t[i] - self.x_t[i]) * self.K[i]
		u = (u0 - self.x_t[self.order]) / self.b0
		'''
		if u[0] < 0:
			u[0] = 0
		elif u[0] > 1:
			u[0] = 1
		'''
		with open(self.filename, 'a+') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writerow({'t': self.t(), 'r(t)' : self.r(0), 'y(t)' : self.y(0), 'u(t)' : u[0]})
		return u[0]