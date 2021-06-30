import matplotlib.pyplot as plt
import pandas as pd
import os
from pandas.core.frame import DataFrame

performance = {'Kp': [], 'Ki': [], 'Kd': [], 'iae': [], 'ise': [], 'itae': [],
                'goodhart': [], 'rbemce': [], 'rbmsemce': [], 'variability': []}

if os.path.isdir("sim_data_pid") and len(os.listdir("sim_data_pid")) > 0:

    if not os.path.isdir("plot_data_pid"):
        os.mkdir("plot_data_pid")

    for x in os.listdir("./sim_data_pid"):

        if x.endswith(".csv"):

            kp, ki, kd = x.split('_')[:3]
            performance['Kp'].append(kp)
            performance['Ki'].append(ki)
            performance['Kd'].append(kd)

            df = pd.read_csv("./sim_data_pid/" + x)
            df = df[df['t'] < 180]
            t = df['t']
            r = df['r(t)']
            y = df['y(t)']
            u = df['u(t)']

            plt.plot(t, y, 'r', t, r, '--g')
            plt.xlabel('tempo(s)')
            plt.legend(['saída - y(t)', 'referência - r(t)'])
            plt.title('PID' + ' - Kp: ' + str(kp) + ', Ki: ' + str(ki) + ', Kd: ' + str(kd))
            plt.savefig("./plot_data_pid/output_" + str(kp) + "_" + str(ki) + "_" + str(kd) + ".png")
            plt.clf()

            plt.plot(t, u, 'b')
            plt.xlabel('tempo(s)')
            plt.legend(['sinal de controle - u(t)'])
            plt.title('PID' + ' - Kp: ' + str(kp) + ', Ki: ' + str(ki) + ', Kd: ' + str(kd))
            plt.savefig("./plot_data_pid/control_" + str(kp) + "_" + str(ki) + "_" + str(kd) + ".png")
            plt.clf()

            e = r - y
            N = len(e)

            iae = sum(abs(e)) / N
            performance['iae'].append(iae)
            ise = sum(e**2) / N
            performance['ise'].append(ise)
            itae = sum(t * abs(e)) / N
            performance['itae'].append(itae)

            alpha1 = 0.3
            alpha2 = 0.5
            alpha3 = 0.2

            e1 = sum(u) / N
            e2 = sum((u - e1)**2) / N
            e3 = iae

            goodhart = alpha1 * e1 + alpha2 * e2 + alpha3 * e3
            performance['goodhart'].append(goodhart)

            beta = 1.5

            rbemce = iae + (beta / N) * sum(u)
            performance['rbemce'].append(rbemce)
            rbmsemce = ise + (beta / N) * sum(u)
            performance['rbmsemce'].append(rbmsemce)

            mu = sum(y) / N
            sigma = (sum((y - mu)**2) / N) ** 0.5
            variability = 2 * sigma / mu
            performance['variability'].append(variability)

    df = DataFrame(performance)
    df.to_csv('performance_data_pid.csv', index=False)

else:
    print("No results to plot and evaluate.")