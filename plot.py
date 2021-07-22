import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from pandas.core.frame import DataFrame

system = "TANK"
currentdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.join(currentdir, system)
plotdir = currentdir

if os.path.isdir(datadir) and len(os.listdir(datadir)) > 0:

    fig_titles = []

    for x in os.listdir(datadir):

        if x.endswith(".csv"):

            tp = x.split('_')

            if len(tp) == 4:
                title = 'PID'
                zorder = 10
                typeline = '-.'
            else:
                title = 'ADRC Linear Ordem ' + tp[0]
                if tp[0] == '1':
                    zorder = 20
                    typeline = '-.'
                else:
                    zorder = 0
                    typeline = '-.'

            fig_titles.append(title)

            df = pd.read_csv(datadir + "/" + x)
            t = df['t']
            r = df['r(t)']
            y = df['y(t)']
            u = df['u(t)']

            plt.figure(1)
            plt.plot(t, u, typeline, zorder=zorder)

            plt.figure(2)
            plt.plot(t, y, typeline, zorder=zorder)

    plt.figure(1)
    plt.xlabel('tempo(s)')
    plt.ylabel('abertura da válvula de entrada (%)')
    plt.title('Sinal de controle - u(t)')
    plt.ylim(-0.05, 1.18)
    plt.xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    plt.legend(fig_titles)
    plt.savefig(plotdir + "/control" + system + ".png")

    fig_titles.append('Set Point')
    plt.figure(2)
    plt.plot(t, r, '--', zorder=30)
    plt.xlabel('tempo(s)')
    plt.ylabel('altura da coluna de líquido (m)')
    plt.title('Resposta do sistema - y(t)')
    plt.xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    plt.legend(fig_titles)
    plt.savefig(plotdir + "/output" + system + ".png")

    plt.clf()
            

else:
    print("No data to plot")
