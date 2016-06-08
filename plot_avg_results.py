# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================

import csv
import os
from function_def import *

#==============================================================================
# Reads in, plots average simulation data
#==============================================================================

num_ticks = 50
num_nodes = 500

os.chdir("C:/path/to/file/sim1")

data = []

with open("mean_results.csv", "rb") as csvfile:
    csvreader = csv.reader(csvfile, delimiter = ',')
    for row in csvreader:
        data.append(list(row))

# changing data type from string to float
green = [float(i) for i in data[0]]
yellow = [float(i) for i in data[1]]
orange = [float(i) for i in data[2]]
red = [float(i) for i in data[3]]
gov_rs = [float(i) for i in data[4]]
media_rs = [float(i) for i in data[5]]
grid_rs = [float(i) for i in data[6]]
neighbour_rs = [float(i) for i in data[7]]
avg_rp = [float(i) for i in data[8]]

plot_stack(green, yellow, orange, red, num_ticks, num_nodes, True)
plot_rs_sent(gov_rs, media_rs, neighbour_rs, grid_rs, avg_rp, num_ticks, True)

