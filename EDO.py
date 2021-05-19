from math import *
import numpy as np

def rungekutta4(t, A, B, L, x, u, y):
    dx = np.matmul(A, x) + B * u + L * y
    k1 = t * dx
    aux = x + 0.5 * k1

    dx2 = np.matmul(A, aux) + B * u + L * y
    k2 = t * dx2
    aux2 = x + 0.5 * k2

    dx3 = np.matmul(A, aux2) + B * u + L * y
    k3 = t * dx3
    aux3 = x + k3

    dx4 = np.matmul(A, aux3) + B * u + L * y
    k4 = t * dx4

    x_next = x + (1/6) * (k1 + 2*k2 + 2*k3 + k4)

    return x_next