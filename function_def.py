# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================

import random as rnd
import networkx as nx
import matplotlib as mpl
from agent_class_def import *

#==============================================================================
# Functions - plotting
#==============================================================================

def network_plot(H, random = True, save = False, diff_color = True):                 
    """
    Overview
    -----------------
    This is used to plot social network graphs
    
    Input
    -----------------
    H is assumed to be a networkx network graph    
    
    if random is False, display mechanism will use default networkx
    representation of graph
    
    save designates whether the plot should be saved to file
    
    diff_color designates whether the plot should include different colors
    of agents or not
    """    
    color_array = []
    label_dict = {}
    
    for node in H.nodes():
        color_array.append(node.get_color())
                    
        label_dict[node] = node.get_name()
        
    if random and diff_color:
        nx.draw_random(H, node_color = color_array, labels = label_dict)  
    elif random and not diff_color:
        nx.draw_random(H, labels = label_dict)
    elif not random and diff_color:
        nx.draw(H, node_color = color_array, labels = label_dict)
    elif not random and not diff_color:
        nx.draw(H, labels = label_dict)
        
    if save:
        mpl.pyplot.savefig("social_network_graph.png")
    mpl.pyplot.show()


def plot_lines(green, yellow, orange, red, xlim, ylim, save = False):
    """
    This plots the changes in numbers according to level
    of risk perception over time
    """    
    x = [i for i in range(len(green))]
    
    fig = mpl.pyplot.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, green, "g-",
             x, yellow, "y-",
             x, orange, "orange",
             x, red, "r-")
    ax1.set_xlabel("time steps")
    ax1.set_ylabel("number of agents")
    ax1.set_title("risk perception over time")
    mpl.pyplot.show()
                    
def plot_stack(green, yellow, orange, red, xlim, ylim, save = False):
    """
    Does the same as plot_data() but produces stackplot instead
    """    
    x = [i for i in range(len(green))]
    
    mpl.pyplot.xlim(0, xlim)
    mpl.pyplot.ylim(0, ylim)
    mpl.pyplot.stackplot(x, green, yellow, orange, red, colors = ["green",\
                "yellow", "orange", "red"])

    # proxy Rectangles for legend only
    low = mpl.patches.Rectangle((0, 0), 1, 1, fc = "green")
    medium = mpl.patches.Rectangle((0, 0), 1, 1, fc = "yellow")
    heightened = mpl.patches.Rectangle((0, 0), 1, 1, fc = "orange")
    high = mpl.patches.Rectangle((0, 0), 1, 1, fc = "red")
    
    mpl.pyplot.legend((low, medium, heightened, high), ("low", "medium", 
                                             "heightened", "high"),
                                             loc = 4)
    mpl.pyplot.xlabel("time steps")
    mpl.pyplot.ylabel("number of agents")
    mpl.pyplot.title("risk perception over time, stackplot")
    if save:
        mpl.pyplot.savefig("stackplot.png")
    mpl.pyplot.show()
    
def plot_rs_sent(gov_rs, media_rs, neighbour_rs, grid_rs, 
                 avg_rp, xlim, save = False):
    """
    Plots the risk signals sent out by different sources
    together with the average risk perception
    """
    x = [i for i in range(len(gov_rs))]
        
    fig = mpl.pyplot.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, gov_rs, "g",
             x, media_rs, "b",
             x, neighbour_rs, "r",
             x, grid_rs, "y",
             [], [], "black")    # empty line to make legend work
    ax1.set_xlabel("time steps")
    ax1.set_ylabel("number of risk signals")
    ax1.set_xlim(0, xlim)
    ax1.set_title("# of risk signals sent and average risk perception")
    mpl.pyplot.legend(("Gov.", "Media",
                   "Neighb.", "Grid", "Avg. RP"), loc = 1)
    ax2 = ax1.twinx()
    ax2.plot(x, avg_rp, "black")
    ax2.set_ylabel("risk perception")
    if save:
        mpl.pyplot.savefig("rs_sent.png")
    mpl.pyplot.show()
    
#==============================================================================
# Functions - graphs
#==============================================================================

def _random_subset(seq, m):
    """
    Returns random subset of seq of length m
    Based on function from networkx Python module
    """
    targets = set()
    while len(targets) < m:
        x = rnd.choice(seq)
        targets.add(x)
    return targets
    
    
def barabasi_albert(AgentClass, n, m, seed = None):
    """
    Creates Barabasi-Albert graph/network
    Based on function from networkx Python module
    
    AgentClass is assumed to be an object type (not instance) that 
    is supposed to make up the nodes in the network
    """
            
    social_network = nx.Graph()
    for i in range(m):
        social_network.add_node(AgentClass(i))
        
    targets = social_network.nodes()
    
    repeated_nodes = []
    
    source = m
    
    while source < n:
        local_agent = AgentClass(source)
        social_network.add_edges_from(zip([local_agent] * m, targets))
        repeated_nodes.extend(targets)
        repeated_nodes.extend([local_agent] * m)
        targets = _random_subset(repeated_nodes, m)
        source += 1
        
    return social_network