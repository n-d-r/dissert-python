# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================
import networkx as nx
import numpy as np
from function_def import *
import os
import matplotlib as mpl

#==============================================================================
# Create example network and plot for demonstrative purposes
#==============================================================================

os.chdir("C:/path/where/to/save/file")

ba = barabasi_albert(Agent, 100, 3)
avg_degree = np.mean(ba.degree(ba.nodes()).values())

K = {node.get_name(): [node.get_risk_perception(), ba.degree(node)] 
    for node in ba.nodes()}
        
RP = [node[0] for node in K.values()]
DG = [node[1] for node in K.values()]

color = [node.color for node in social_network.nodes()]

network_plot(ba, random = False, diff_color = True, save = True)

fig = mpl.pyplot.figure()
ax = fig.add_subplot(111)
ax.scatter(DG, range(len(DG)), c = color)
ax.set_title("degree scatterplot")
ax.set_xlabel("degree")
ax.set_ylabel("agent number")
mpl.pyplot.savefig("degree_scatterplot.png")
mpl.pyplot.show()