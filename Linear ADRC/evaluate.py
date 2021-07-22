import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from pandas.core.frame import DataFrame

# This will name the folder to store simulation data.
system = "tank"
currentdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.join(currentdir, ("data_" + system))

#Dictionary to store simulation performance indexes.
performance = {'order': [], 'b0': [], 's_cl': [], 's_eso': [], 'R': [], 'iae': [], 'ise': [], 'itae': [],
                'goodhart': [], 'rbemce': [], 'rbmsemce': [], 'variability': []}

if os.path.isdir(datadir) and len(os.listdir(datadir)) > 0:
    # if there are files on directory, it reads all CSV files.
    for x in os.listdir(datadir):

        if x.endswith(".csv"):
            #Appends the ADRC parameters to dict.
            order, b0, s_cl, s_eso, R = x.split('_')[:5]
            performance['order'].append(order)
            performance['b0'].append(b0)
            performance['s_cl'].append(s_cl)
            performance['s_eso'].append(s_eso)
            performance['R'].append(R)

            # Read the simulation data values.
            df = pd.read_csv(datadir + "/" + x)
            t = df['t']
            r = df['r(t)']
            y = df['y(t)']
            u = df['u(t)']

            e = r - y
            N = len(e)

            # Calculate IAE, ISE and ITAE indexes.
            iae = sum(abs(e)) / N
            performance['iae'].append(iae)
            ise = sum(e**2) / N
            performance['ise'].append(ise)
            itae = sum(t * abs(e)) / N
            performance['itae'].append(itae)

            #Calculate Goodhart Index.
            alpha1 = 0.3
            alpha2 = 0.5
            alpha3 = 0.2

            e1 = sum(u) / N
            e2 = sum((u - e1)**2) / N
            e3 = iae

            goodhart = alpha1 * e1 + alpha2 * e2 + alpha3 * e3
            performance['goodhart'].append(goodhart)

            #Calculate RBEMCE and RBMSEMCE
            beta = 1

            rbemce = iae + (beta / N) * sum(u)
            performance['rbemce'].append(rbemce)
            rbmsemce = ise + (beta / N) * sum(u)
            performance['rbmsemce'].append(rbmsemce)

            #Calculate variability of system response
            mu = sum(y) / N
            sigma = (sum((y - mu)**2) / N) ** 0.5
            variability = 2 * sigma / mu
            performance['variability'].append(variability)

    #Write all performance indexes on a CSV file.
    df = DataFrame(performance)
    df.to_csv(currentdir + '/performance_' + system  + '.csv', index=False)

else:
    print("No data to plot and evaluate.")
