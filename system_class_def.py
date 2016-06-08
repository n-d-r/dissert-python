# -*- coding: utf-8 -*-

#==============================================================================
# Imports
#==============================================================================

import networkx as nx
import matplotlib as mpl
import random as rnd
from function_def import *
from agent_class_def import *

#==============================================================================
# Simulation class
#==============================================================================

class Simulation:
    """
    Main class that runs the simulation
    """
    def __init__(self):
        """
        Overview
        ---------------
        Initialisation. Risk signals sent out by the government, the grid
        and by neighbours in the network are recorded here. Risk signals
        sent out by the Media are recorded in Media object instance
        """
        self.gov_risk_signals = 0
        self.neighbour_risk_signals = 0
        self.grid_risk_signals = 0
        self.HazardHappened = False
        self.MediaIntensity = 0
                
    def init_network(self, network):
        """
        network can be any kind of (social) network graph
        """
        self.network = network
        
    def init_institutions(self, 
                          MediaClass, 
                          GovernmentClass, GovernmentMultiplier,
                          HazardClass, HazardName, HazardMultiplier):
        """
        Overview
        ---------------
        Simply creates and initializes the institutions that
        are not part of the network graph but send out risk 
        signals to agents in the graph
        
        Input
        ---------------
        The input are the scenario parameters used in a particular run:
        GovernmentClass: Government object instance
        GovernmentMultiplier: assumed to be between .1 and 2.0
        HazardClass: Hazard object instance
        HazardName: name of Hazard object instance
        HazardMultiplier: assumed to be between .1 and 2.0
        """
        self.Media = MediaClass("Media")
        self.Government = GovernmentClass("Government", GovernmentMultiplier)
        self.Hazard = HazardClass("%s" % HazardName, HazardMultiplier)
        
    def init_parameters(self, num_ticks, hazard_triggered, num_affected,
            MediaDelay, MediaMultiplier, MediaReportingIntensity,
            GovernmentStop, GovernmentDelay, verbose = False):
        """
        Overview
        ---------------
        Initializes relevant parameters that are used in other functions;
        verbose allows to check on initialisation
        
        Input
        ---------------
        num_ticks: number of ticks/time steps the simulation should run
        hazard_triggered: time step at which the hazard event happens
        num_affected: number of nodes affected by the hazard event
        MediaDelay: the number of timesteps the media response is delayed
                    after the initial hazard event happened
        MediaMultiplier: between .1 and 2.0
        MediaReportingIntensity: between .0 and 1.0, probability of a node
                    receiving media risk signals via reporting
        GovernmentStop: time step at which governemnt communications stop
        GovernmentDelay: delay of government response
        """
        self.num_ticks = num_ticks
        self.hazard_triggered = hazard_triggered
        self.num_affected = num_affected
        self.MediaDelay = MediaDelay
        self.MediaMultiplier = MediaMultiplier
        self.MediaReportingIntensity = MediaReportingIntensity
        self.GovernmentStop = GovernmentStop
        self.GovernmentDelay = GovernmentDelay
                        
        if verbose:
            print "num_ticks:", self.num_ticks
            print "hazard_triggered:", self.hazard_triggered
            print "num_affected:", self.num_affected
            print "MediaDelay:", self.MediaDelay
            print "MediaMultiplier:", self.MediaMultiplier
            print "MediaReportingIntensity:", self.MediaReportingIntensity
            print "GovernmentStop:", self.GovernmentStop
            print "GovernmentDelay:", self.GovernmentDelay
              
    def return_network(self):
        """
        Returns the current network state to make it available for plotting
        """        
        return self.network              
              
    def report_state(self):
        """
        Overview
        ---------------
        Reports the current state of all relevant variables
        
        Output
        ---------------
        Dictionary with data summarizing current Simulation state, assumed
        to be passed to SystemState object instance's record_data() function
        """
        tmp_status_dict = {}
        tmp_rp_lst = []         # risk perceptions
        num_rs_sent = []        # risk signals sent
        for node in self.network:
            # get color of node
            tmp_status_dict[node.get_name()] = node.get_color()
            
            # get risk perception of node
            tmp_rp_lst.append(node.get_risk_perception())
            
            # get number of risk signals sent by node
            num_rs_sent.append(node.get_rs_sent())
            
        # counts occurances of colors in the status_dict
        curr_green = tmp_status_dict.values().count("green")
        curr_yellow = tmp_status_dict.values().count("yellow")
        curr_orange = tmp_status_dict.values().count("orange")
        curr_red = tmp_status_dict.values().count("red")
                    
        # data about the number of risk signals sent
        # by different institutions and agents
        neighbour_num_rs_sent = sum(num_rs_sent)                    
        gov_num_rs_sent = self.gov_risk_signals
        media_num_rs_sent = self.Media.get_rs_sent()    # also resets counter
        grid_num_rs_sent = self.grid_risk_signals
        
        # reset risk signal counters
        self.gov_risk_signals = 0
        self.grid_risk_signals = 0
                    
        # current average risk perception is needed later on
        # for the Media to react to therefore it's recorded
        # internally as well for later access in tick()
        self.curr_avg_rp = np.mean(tmp_rp_lst)                    
                    
        return dict([("curr_green", curr_green),
                     ("curr_yellow", curr_yellow),
                     ("curr_orange", curr_orange),
                     ("curr_red", curr_red),
                     ("curr_avg_rp", self.curr_avg_rp),
                     ("gov_rs_sent", gov_num_rs_sent), 
                     ("media_rs_sent", media_num_rs_sent),
                     ("neighbour_rs_sent", neighbour_num_rs_sent),
                     ("grid_rs_sent", grid_num_rs_sent)])
    
    def report_rs_sent_received(self):
        """
        Reports the number of risk signals sent and received by all nodes
        after a simulation run. Output is a dictionary
        """
        outdict = {}        
        for node in self.network:
            outdict[node.get_name()] = (self.network.degree(node), 
                                        node.get_rs_end_state()[0], # sent
                                        node.get_rs_end_state()[1]) # received
        return outdict
    
    def tick(self, tick):
        """
        Overview
        ---------------
        Behaviour for the whole simulation at each tick/time step
        
        Input
        ---------------
        tick: current tick/time step being executed
        """
        # local copy of nodes so that they don't get deleted (see below)
        # from the actual graph
        self.local_nodes = self.network.nodes()
    
        # tick/time step at which the hazard event is triggered
        if tick == self.hazard_triggered:
            self.HazardHappened = True
            self.affected_by_hazard = rnd.sample(self.local_nodes, 
                                                 self.num_affected)
            for agent in self.affected_by_hazard:
                agent.add_risk_signal(RiskSignal("grid",
                                            self.Hazard.get_rp_multiplier()))
            self.grid_risk_signals += len(self.affected_by_hazard)
        
        # Media starts reporting on the hazard event
        if tick == self.hazard_triggered + self.MediaDelay:
            self.Media.start_reporting(self.MediaMultiplier)
            self.Media.set_intensity(self.MediaReportingIntensity)
            
        # period in which Government communicates about hazard event
        # commented code allows change between continuous and permanent comms
        if self.GovernmentStop > tick >= self.GovernmentDelay:
#        if tick >= self.GovernmentDelay:
#            if (tick - self.GovernmentDelay)%4 == 0:
                self.Government.send_risk_signal(self.network.nodes(), 
                                                 self.Hazard)
                self.gov_risk_signals += len(self.network.nodes())
            
        # Media behaviour for each tick/time step
        if self.Media.reports:
            self.Media.tick_behaviour(self.curr_avg_rp)
            self.MediaIntensity = self.Media.get_intensity()
        
        # activates each node in turn and triggers tick behaviour,
        # no set order exists to eliminate first-mover biases
        for index in range(len(self.network.nodes())):
            self.active_node = rnd.choice(self.local_nodes)
            self.active_node.tick_behaviour(self.Media, self.Government,
                                       self.Hazard)
            self.local_nodes.remove(self.active_node)
        
        
#==============================================================================
# SystemState class    
#==============================================================================
    
class SystemState:
    """
    Overview
    ---------------
    Class to save the state of the simulation at each time step,
    can output final lists of data to file
    """
#    def __init__(self, network):
    def __init__(self):
        """
        Overview
        ---------------
        Empty lists for all variables that are recorded with Simulation
        object's report_data() function and passed to SystemState
        record_data() function
        """
        self.green = []
        self.yellow = []
        self.orange = []
        self.red = []
        self.gov_rs = []
        self.media_rs = []
        self.grid_rs = []
        self.neighbour_rs = []
        self.avg_rp = []
        
    def record_data(self, data_dict):
        """
        Overview
        ---------------
        Takes in data and appends it to the appropriate lists to record data
        over time
        
        Input
        ---------------
        data_dict is assumed to be a dictionary passed from report_data() 
        function of a Simulation object
        """
        self.green.append(data_dict["curr_green"])
        self.yellow.append(data_dict["curr_yellow"])
        self.orange.append(data_dict["curr_orange"])
        self.red.append(data_dict["curr_red"])
        self.gov_rs.append(data_dict["gov_rs_sent"])
        self.media_rs.append(data_dict["media_rs_sent"])
        self.grid_rs.append(data_dict["grid_rs_sent"])
        self.neighbour_rs.append(data_dict["neighbour_rs_sent"])
        self.avg_rp.append(data_dict["curr_avg_rp"])

    def return_data(self):
        """
        Returns dictionary with all data recorded so far 
        """
        return {"green": self.green,
                "yellow": self.yellow,
                "orange": self.orange,
                "red": self.red,
                "gov_rs": self.gov_rs,
                "media_rs": self.media_rs,
                "grid_rs": self.grid_rs,
                "neighbour_rs": self.neighbour_rs,
                "avg_rp": self.avg_rp}

    def save_data(self, num_run, verbose = False):
        """
        Saves lists of data with length equal to number of ticks/time steps
        in a file named after the number of the current run of the simulation
        """
        outfile = open("%s.csv" % num_run, "w")
        if verbose:
            outfile.write('green, ' + ''.join(str(self.green).strip('[]')) + '\n')
            outfile.write('yellow, ' + ''.join(str(self.yellow).strip('[]')) + '\n')
            outfile.write('orange, ' + ''.join(str(self.orange).strip('[]')) + '\n')
            outfile.write('red, ' + ''.join(str(self.red).strip('[]')) + '\n')
            outfile.write('gov_rs, ' + ''.join(str(self.gov_rs).strip('[]')) + '\n')
            outfile.write('media_rs, ' + ''.join(str(self.media_rs).strip('[]')) + '\n')
            outfile.write('grid_rs, ' + ''.join(str(self.grid_rs).strip('[]')) + '\n')
            outfile.write('neighbour_rs, ' + ''.join(str(self.neighbour_rs).strip('[]')) + '\n')
            outfile.write('avg_rp, ' + ''.join(str(self.avg_rp).strip('[]')) + '\n')
        else:
            outfile.write(''.join(str(self.green).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.yellow).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.orange).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.red).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.gov_rs).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.media_rs).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.grid_rs).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.neighbour_rs).strip('[] ')) + '\n')
            outfile.write(''.join(str(self.avg_rp).strip('[] ')) + '\n')
        outfile.close()

