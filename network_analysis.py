# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================

from function_def import *

#==============================================================================
# Generating network ties and Euclidean distance matrices
#==============================================================================

def network_analysis(network, when):
    """
    network: assumed to be a network from networkx
    when: indicates whether function is called prior or after execution
    of a simulation/run; only saves adjacency matrix if executed before
    simulation/run
    """
    L = [[0 for i in range(len(network.nodes()))] for j in range(len(network.nodes()))]
    RP = [[0 for i in range(len(network.nodes()))] for j in range(len(network.nodes()))]
    
    for edge in network.edges():
        i = network.nodes().index(edge[0])
        j = network.nodes().index(edge[1])
        L[i][j] = 1
        L[j][i] = 1
    
    for i in range(len(network.nodes())):
        for j in range(len(network.nodes())):
            if network.nodes()[i].risk_perception > \
               network.nodes()[j].risk_perception:
                   RP[i][j] = network.nodes()[i].risk_perception - \
                              network.nodes()[j].risk_perception
            else:
                RP[i][j] = network.nodes()[j].risk_perception - \
                           network.nodes()[i].risk_perception
    
    counter = 0
    for i in L:
        counter += sum(i)
    
    if when == "before":
        out1 = open("network_ties.csv", "w")
        for i in L:
            out1.write(''.join(str(i).strip('[] ') + '\n'))
        out1.close()
        
        out2 = open("distance_before.csv", "w")
        for j in RP:
            out2.write(''.join(str(j).strip('[] ') + '\n'))
        out2.close()
    elif when == "after":
        # network ties don't change so only need new distance
        out2 = open("distance_after.csv", "w")
        for j in RP:
            out2.write(''.join(str(j).strip('[] ') + '\n'))
        out2.close()

