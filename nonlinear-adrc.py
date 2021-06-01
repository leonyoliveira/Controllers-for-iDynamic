from ControlLib import *
from runkut4_adrc import *
from functools import partial
import numpy as np
import csv

class NonlinearADRC(Control): 

	def __init__(self, T, order, R, delta, alpha, beta, beta_obs, b0):
		super().__init__(T=T, order=order)
		self.R = R
		self.delta = delta
		self.alpha = alpha
		self.beta = beta
		self.beta_obs = beta_obs
		self.b0 = b0
		self.v_t = np.zeros((2, 1))
		self.x_t = np.zeros((3, 1))
		self.filename = "sim_results_adrc/n_"
		'''
		with open(self.filename, 'w') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writeheader()
		'''

	def control(self):
		nltd = partial(nonlinear_tracking_differentiator, self.r(), self.R)
		self.v_t = runkut4(nltd, self.v_t, self.T)
		nleso = partial(nonlinear_extended_state_observer, self.beta_obs, self.u(), self.y(), self.delta, self.b0)
		self.x_t = runkut4(nleso, self.x_t, self.T)
		u0 = 0
		for i in range(2):
			u0 += self.beta[i] * fal((self.v_t[i][0] - self.x_t[i][0]), self.alpha[i], self.delta)
		u = (u0 - self.x_t[2][0]) / self.b0
		'''
		with open(self.filename, 'a+') as file:
			fields = ['t', 'r(t)', 'y(t)', 'u(t)']
			writer = csv.DictWriter(file, fieldnames=fields)
			writer.writerow({'t': self.t(), 'r(t)' : self.r(0), 'y(t)' : self.y(0), 'u(t)' : u[0]})
		'''
		return u

print("Define R parameter for TD maximum acceleration speed:")
R = int(input())
print("Define delta parameter for fal function:")
delta = float(input())
print("Define two alpha values for the fal function applied to control law (splitted by comma):")
alpha = [float(x) for x in input().split(',')]
print("Define two beta values for control law gains (splitted by comma):")
beta = [float(x) for x in input().split(',')]
print("Define three beta_o values for observer gains (splitted by comma):")
beta_obs = [float(x) for x in input().split(',')]
print("Define b0 parameter:")
b0 = float(input())

controller = NonlinearADRC(T=0.1, order=3, R=R, delta=delta, alpha=alpha, beta=beta, beta_obs= beta_obs, b0=b0)
rc = RemoteControl(controller)
rc.run()