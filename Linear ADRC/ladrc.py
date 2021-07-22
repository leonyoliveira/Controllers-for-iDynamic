import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

# This will name the folder to store simulation data.
system = "tank"
datadir = os.path.join(currentdir, ("data_" + system))

import random
from ControlLib import *
from runkut4_adrc import *
from functools import partial
import numpy as np
import math
import csv

class LADRC(Control): 

	def __init__(self, T, order, adrc_order, s_cl, s_eso, b0, R):
		super().__init__(T=T, order=order)
		# Definition of ADRC parameters.
		self.update_LADRC(adrc_order, s_cl, s_eso, b0, R)
		# Creating two arrays of zeros to calculate the states of Tracking Differentiator and Extended State Observer.
		self.v_t = np.zeros((self.adrc_order, 1))
		self.x_t = np.zeros((self.adrc_order+1, 1))
		# Some flags used on simulation with iDynamic.
		self.sp = -1
		self.stop_flag = 0
		self.sim = 1
		# Creates the file for simulation data. 
		self.filename = datadir + "/" + str(adrc_order) + "_" + str(b0) + "_" + str(s_cl) + "_" + str(s_eso) + "_" + str(R) + "_" + ".csv"
		if not os.path.isdir(datadir):
			os.mkdir(datadir)
		with open(self.filename, 'w') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writeheader()

	def update_LADRC(self, adrc_order, s_cl, s_eso, b0, R):
		# This function is called everytime the server is initiated or updated. The parameters and matrixes of controller are updated
		# with new values.
		self.adrc_order = adrc_order
		self.s_cl = s_cl
		self.s_eso = s_eso
		self.b0 = b0
		self.R = R
		self.A, self.B, self.C, self.A_td, self.B_td, self.K, self.L = self.ADRC_matrices()

	def update_setpoint(self, sp):
		# function called to update set point value to iDynamic, it's called by the GUI.
		self.sp = sp

	def stop_press(self):
		# function called by GUI to stop server.
		self.stop_flag = 1

	def ADRC_matrices(self):
		'''
		Here, all ADRC matrixes are initiated with zeros and calculated iteratively from the choosed order.
		A, B and C are reffering to the system on state-space form.
		K calculate the controller gains.
		L calculate the observer gains.
		A_td and B_td are Tracking Differentiator matrixes.
		'''
		A = np.zeros((self.adrc_order+1, self.adrc_order+1))
		B = np.vstack((np.zeros((self.adrc_order-1, 1)), self.b0, 0))
		C = np.hstack((1, np.zeros(self.adrc_order)))
		K = np.zeros(self.adrc_order)
		L = np.zeros((self.adrc_order+1, 1))
		A_td = np.zeros((self.adrc_order, self.adrc_order))
		B_td = np.vstack((np.zeros((self.adrc_order-1, 1)), self.R**self.adrc_order))
		for i in range(self.adrc_order):
			if i < self.adrc_order-1:
				A_td[i][i+1] = 1.
			A_td[self.adrc_order-1][i] = -math.comb(self.adrc_order, i) * self.R ** (self.adrc_order-i)
			A[i][i+1] = 1.
			K[i] = math.comb(self.adrc_order, self.adrc_order-i) * math.pow(self.s_cl, self.adrc_order-i)
			L[i][0] = math.comb(self.adrc_order+1, i+1) * math.pow(self.s_eso, i+1)
		L[self.adrc_order][0] = math.comb(self.adrc_order+1, self.adrc_order+1) * math.pow(self.s_eso, self.adrc_order+1)
		return A, B, C, A_td, B_td, K, L

	def set_point(self):
		return self.sp

	def stop(self):
		return self.stop_flag

	def control(self):
		'''
		This function will calculate the control signal.
		First, all previous and current values are stored, an internal noise is added on system response.
		After it, twenty intermediary points are calculated using linear interpolation, for each point, the control signal is calculated.
		Then, all values are stored on a CSV file, and the control signal is returned.
		'''
		prev_y = self.y(-1)
		curr_y = self.y() + random.uniform(-0.05,0.05) * self.r()
		curr_u = self.u()
		prev_r = self.r(-1)
		curr_r = self.r()
		curr_t = self.t()
		prev_t = curr_t - self.T

		for i in range(1,20):
			T_aux = self.T/20
			t_aux = prev_t + i * T_aux
			y_aux = prev_y + (((t_aux - prev_t) / (curr_t - prev_t)) * (curr_y - prev_y))
			r_aux = prev_r + (((t_aux - prev_t) / (curr_t - prev_t)) * (curr_r - prev_r))
			ltd = partial(linear_tracking_differentiator, self.A_td, self.B_td, r_aux)
			self.v_t = runkut4(ltd, self.v_t, T_aux)
			leso = partial(linear_extended_state_observer, self.A, self.B, self.L, curr_u, y_aux)
			self.x_t = runkut4(leso, self.x_t, T_aux)

			u0 = 0
			for i in range(self.adrc_order):
				u0 += (self.v_t[i] - self.x_t[i]) * self.K[i]
			u = (u0 - self.x_t[self.adrc_order]) / self.b0
			
			'''
			# Used only on Liquid Level Control on iDynamic.
			if u[0] < 0:
				u[0] = 0
			elif u[0] > 1:
				u[0] = 1
			'''

			curr_u = u[0]
			
		with open(self.filename, 'a+') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writerow({'t': round(self.t(),1), 'r(t)' : self.r(0), 'y(t)' : self.y(0), 'u(t)' : u[0]})
		return curr_u