import os, sys
import random
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
system = "temp"
datadir = os.path.join(currentdir, ("data_" + system))

from ControlLib import *
import csv

class PID(Control): 
    def __init__(self, T, order, Kp, Ki, Kd):
        super().__init__(T=T, order=order)
        self.update_gains(Kp, Ki, Kd)
        self.int_error = 0
        self.sp = -1
        self.stop_flag = 0
        self.prev_error = 0
        self.filename = datadir + "/" + str(Kp) + "_" + str(Ki) + "_" + str(Kd) + "_" + ".csv"
        if not os.path.isdir(datadir):
            os.mkdir(datadir)
        with open(self.filename, 'w') as file:
            fields = ['t', 'r(t)', 'y(t)', 'u(t)']
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

    def stop(self):
        return self.stop_flag

    def stop_press(self):
        self.stop_flag = 1

    def update_setpoint(self, sp):
        self.sp = sp

    def update_gains(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

    def set_point(self):
        return self.sp

    def control(self):
        yn = self.y() + random.uniform(-0.05,0.05) * self.r()
        err = self.r() - yn
        self.int_error += (err * self.T)
        P = self.Kp * err
        I = self.Ki * self.int_error
        D = self.Kd * (err - self.prev_error) / self.T
        u = P + I + D
        self.prev_error = err
        with open(self.filename, 'a+') as file:
            fields = ['t', 'r(t)', 'y(t)', 'u(t)']
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writerow({'t': self.t(), 'r(t)' : self.r(0), 'y(t)' : self.y(0), 'u(t)' : u})
        return u
