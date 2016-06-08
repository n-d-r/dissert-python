# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================

import random as rnd
import networkx as nx
import matplotlib as mpl
import sys
from system_class_def import *
from agent_class_def import *
from function_def import *
from network_analysis import *

#==============================================================================
# Parameters
#==============================================================================

num_nodes = 100
num_edges = 3
num_ticks = 50
num_runs = 1
hazard_triggered = 1
num_affected = 20

# rescaled first component scores of hazard scenarios
HazardDict = {"Automation": 1.3, 
              "Meter Reading": 0.89867133572128, 
              "Remote Connect": 1.19725205261451,
              "Outage Detection": 0.7,
              "Power Theft": 0.976680716275362,
              "Pricing": 0.813628981657745,
              "Customer Information": 0.875750820478405,
              "Distributed Resources": 0.937800864934615,
              "Transmissions": 1.10726609072683,
              "Test Value": 1.0}
              

HazardName = "Automation"
HazardMultiplier = HazardDict[HazardName]

GovernmentMultiplier = .4
GovernmentDelay = hazard_triggered + 2
GovernmentStop = GovernmentDelay + 50

MediaMultiplier = 1.2
MediaDelay = 2
MediaReportingIntensity = (num_affected/float(num_nodes))*2

#==============================================================================
# Simulation
#==============================================================================

# uncommment below code and comment out network creation further down in 
# order to run simulation with same starting conditions

#social_network = barabasi_albert(Agent, num_nodes, num_edges)
#for node in social_network.nodes():
#    node.init_neighbors(social_network)


for run in range(num_runs):
    
    # network creation
    social_network = barabasi_albert(Agent, num_nodes, num_edges)
    for node in social_network.nodes():
        node.init_neighbors(social_network)  
    
#    uncomment below code to collect before-run data on network ties and
#    Euclidean distance matrix of differences in risk perceptions
#    network_analysis(social_network, "before")    
    
    Sim = Simulation()
    SimState = SystemState()
    
    Sim.init_network(social_network)
    Sim.init_institutions(Media, Government, GovernmentMultiplier,
                          Hazard, HazardName, HazardMultiplier)
    Sim.init_parameters(num_ticks, hazard_triggered, num_affected,
                        MediaDelay, MediaMultiplier, 
                        MediaReportingIntensity, GovernmentStop,
                        GovernmentDelay, 
                        False)
    
    # record data at beginning of run before any tick behaviour 
    SimState.record_data(Sim.report_state())
    
    for tick in range(num_ticks):
        Sim.tick(tick)
        SimState.record_data(Sim.report_state())
    
    # after each run, save data to file named according to run number
    SimState.save_data("%s" % run)
    
    if num_runs > 1:
        for node in social_network.nodes():
            node.re_initialise()
    else:
        d = Sim.report_rs_sent_received()
#        uncomment below code to record Euclidean distance data after
#        a simulation run
#        network_analysis(social_network, "after")

# Saving the parameters of the current scenario
with open("scenario_parameters.txt", "w") as outfile:
    outfile.write("num_nodes: %s" % num_nodes + '\n')
    outfile.write("num_edges: %s" % num_edges + '\n')
    outfile.write("num_ticks: %s" % num_ticks + '\n')
    outfile.write("num_runs: %s" % num_runs + '\n')
    outfile.write("hazard_triggered: %s" % hazard_triggered + '\n')
    outfile.write("num_affected: %s" % num_affected + '\n')
    outfile.write("HazardMultiplier: %s" % HazardMultiplier + '\n')
    outfile.write("HazardName: %s" % HazardName + '\n')
    outfile.write("GovernmentMultiplier: %s" % GovernmentMultiplier + '\n')
    outfile.write("GovernmentDelay: %s" % GovernmentDelay + '\n')
    outfile.write("GovernmentStop: %s" % GovernmentStop + '\n')
    outfile.write("MediaMultiplier: %s" % MediaMultiplier + '\n')
    outfile.write("MediaDelay: %s" % MediaDelay +  '\n')
    outfile.write("MediaReportingIntensity: %s" % MediaReportingIntensity + '\n')
    