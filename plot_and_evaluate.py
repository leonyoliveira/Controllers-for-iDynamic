import matplotlib.pyplot as plt
import pandas as pd
import os
from pandas.core.frame import DataFrame

performance = {'order': [], 'b0': [], 's_cl': [], 's_eso': [], 'iae': [], 'ise': [], 'itae': [],
                'goodhart': [], 'rbemce': [], 'rbmsemce': [], 'variability': []}

if os.path.isdir("sim_results_adrc") and len(os.listdir("sim_results_adrc")) > 0:

    if not os.path.isdir("plots_adrc"):
        os.mkdir("plots_adrc")

    for x in os.listdir("./sim_results_adrc"):

        if x.endswith(".csv"):

            adrc_ver, order, b0, s_cl, s_eso = x.split('_')[:5]
            performance['order'].append(order)
            performance['b0'].append(b0)
            performance['s_cl'].append(s_cl)
            performance['s_eso'].append(s_eso)

            if adrc_ver == 'l':
                title_ver = "Linear"
            else:
                title_ver = "Não-linear"

            df = pd.read_csv("./sim_results_adrc/" + x)
            df = df[df['t'] < 120]
            t = df['t']
            r = df['r(t)']
            y = df['y(t)']
            u = df['u(t)']

            plt.plot(t, y, 'r', t, r, '--g')
            plt.xlabel('tempo(s)')
            plt.legend(['saída - y(t)', 'referência - r(t)'])
            plt.title('ADRC ' + title_ver + ' - Ordem: ' + str(order) + ', $b_{0}$: ' + str(b0) + ', $s_{CL}$: ' + str(s_cl) + ', $s_{ESO}$: ' + str(s_eso))
            plt.savefig("./plots_adrc/output_" + adrc_ver + str(order) + "_" + str(b0) + "_" + str(s_cl) + "_" + str(s_eso) + ".png")
            plt.clf()

            plt.plot(t, u, 'b')
            plt.xlabel('tempo(s)')
            plt.legend(['sinal de controle - u(t)'])
            plt.title('ADRC ' + title_ver + ' Ordem: ' + str(order) + ', $b_{0}$: ' + str(b0) + ', $s_{CL}$: ' + str(s_cl) + ', $s_{ESO}$: ' + str(s_eso))
            plt.savefig("./plots_adrc/control_" + adrc_ver + str(order) + "_" + str(b0) + "_" + str(s_cl) + "_" + str(s_eso) + ".png")
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
    df.to_csv('performance.csv', index=False)

else:
    print("No results to plot and evaluate.")