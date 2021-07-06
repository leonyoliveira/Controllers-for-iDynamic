from math import *
import numpy as np

def fal(e, alpha, delta):
		if abs(e) > delta:
			return np.sign(e) * (abs(e) ** alpha)
		else:
			return e * (delta ** (alpha - 1))

def linear_tracking_differentiator(A, B, r, v):
    return np.matmul(A, v) + B * r

def linear_extended_state_observer(A, B, L, u, y, x):
    return np.matmul(A, x) + B * u + L * (y - x[0])

def nonlinear_tracking_differentiator(r, R, v):
    v1 = v[1][0]
    v2 = -R * np.tanh(v[0][0] - r + (v[1][0] * (abs(v[1][0]) / (2 * R))))
    return np.array([[v1], [v2]])

def nonlinear_extended_state_observer(beta, u, y, delta, b0, x):
    e = x[0][0] - y
    x1 = x[1][0] - beta[0] * e
    x2 = x[2][0] - beta[1] * fal(e, 0.5, delta) + b0 * u
    x3 = -beta[2] * fal(e, 0.25, delta)
    return np.array([[x1], [x2], [x3]])

def runkut4(func, x, t):
    
    dx1 = func(x)
    k1 = t * dx1
    aux1 = x + 0.5 * k1

    dx2 = func(aux1)
    k2 = t * dx2
    aux2 = x + 0.5 * k2

    dx3 = func(aux2)
    k3 = t * dx3
    aux3 = x + k3

    dx4 = func(aux3)
    k4 = t * dx4

    x_next = x + (1/6) * (k1 + 2*k2 + 2*k3 + k4)

    return x_next
